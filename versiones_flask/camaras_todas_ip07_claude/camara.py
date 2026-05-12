import os
import threading
import time
import logging
from datetime import datetime, date
from pathlib import Path

import cv2


class Camara:
    """
    Encapsula toda la lógica de una cámara IP Tapo:
      - Captura continua de frames via RTSP
      - Grabación diaria de vídeo (rotación automática a medianoche)
      - Eliminación automática de vídeos con más de 7 días
      - Captura de instantáneas bajo demanda

    URL RTSP Tapo:
        stream1 → alta calidad  (por defecto)
        stream2 → calidad estándar
    Puerto por defecto: 554

    IMPORTANTE: el usuario/contraseña son los de la "cuenta de cámara"
    creada en la app Tapo (Ajustes → Avanzado → Cuenta de cámara),
    NO los de tu cuenta TP-Link/Tapo.
    """

    CAPTURAS_DIR   = Path("capturas") / "videos"
    DIAS_RETENCION = 7
    FPS_ESCRITURA  = 15    # FPS del vídeo grabado en disco
    FPS_STREAM     = 15    # FPS máximos enviados al navegador vía MJPEG
    JPEG_CALIDAD   = 80    # Calidad JPEG 0-100
    STREAM         = "stream1"   # "stream1" = alta calidad, "stream2" = baja

    # Variable de entorno que OpenCV lee antes de abrir el stream FFmpeg.
    # Pares  clave;valor  separados por  |
    FFMPEG_OPTIONS = (
        "rtsp_transport;tcp|"
        "stimeout;5000000|"
        "max_delay;500000|"
        "fflags;nobuffer|"
        "flags;low_delay"
    )

    # ------------------------------------------------------------------ #
    # Constructor                                                          #
    # ------------------------------------------------------------------ #

    def __init__(self, cam_dict: dict, logger: logging.Logger | None = None):
        """
        cam_dict debe contener: id, ip, mac, port, user, password
        port suele ser 554 en las Tapo.
        """
        self.id:       str = cam_dict["id"]
        self.ip:       str = cam_dict["ip"]
        self.mac:      str = cam_dict["mac"]
        self.port:     int = int(cam_dict["port"])
        self.user:     str = cam_dict["user"]
        self.password: str = cam_dict["password"]

        self.logger = logger or logging.getLogger(__name__)

        # Último frame JPEG (bytes) — acceso protegido por _lock
        self._frame_bytes: bytes | None = None
        self._lock = threading.Lock()

        # Directorio de vídeos exclusivo de esta cámara
        self.directorio_videos: Path = self.CAPTURAS_DIR / self.id
        self.directorio_videos.mkdir(parents=True, exist_ok=True)

        # Estado de grabación
        self._writer:          cv2.VideoWriter | None = None
        self._fecha_grabacion: date | None            = None
        self._writer_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Propiedades                                                          #
    # ------------------------------------------------------------------ #

    @property
    def rtsp_url(self) -> str:
        """
        Formato oficial Tapo:
            rtsp://usuario:contraseña@IP:554/stream1
        """
        return (
            f"rtsp://{self.user}:{self.password}"
            f"@{self.ip}:{self.port}/{self.STREAM}"
        )

    @property
    def frame_bytes(self) -> bytes | None:
        """Último frame JPEG capturado (thread-safe)."""
        with self._lock:
            return self._frame_bytes

    # ------------------------------------------------------------------ #
    # Arranque                                                             #
    # ------------------------------------------------------------------ #

    def iniciar(self) -> None:
        """Lanza los hilos de captura y limpieza como daemons."""
        threading.Thread(
            target=self._bucle_captura,
            daemon=True,
            name=f"cap-{self.id}",
        ).start()
        threading.Thread(
            target=self._bucle_limpieza,
            daemon=True,
            name=f"clean-{self.id}",
        ).start()
        self.logger.info(f"[{self.id}] Hilos iniciados — URL: {self.rtsp_url}")

    # ------------------------------------------------------------------ #
    # Captura continua                                                     #
    # ------------------------------------------------------------------ #

    def _bucle_captura(self) -> None:
        """Abre el stream RTSP, lee frames y reconecta si cae."""
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.JPEG_CALIDAD]

        while True:
            # OPENCV_FFMPEG_CAPTURE_OPTIONS debe fijarse ANTES de VideoCapture()
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = self.FFMPEG_OPTIONS

            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

            if not cap.isOpened():
                self.logger.warning(
                    f"[{self.id}] No conecta ({self.rtsp_url}) — reintentando en 5 s..."
                )
                cap.release()
                time.sleep(5)
                continue

            self.logger.info(f"[{self.id}] Stream abierto")

            while True:
                ok, frame = cap.read()

                if not ok:
                    self.logger.warning(
                        f"[{self.id}] Perdida de señal — reconectando..."
                    )
                    break

                # Guardar frame como JPEG
                _, buf = cv2.imencode(".jpg", frame, encode_params)
                jpeg = buf.tobytes()
                with self._lock:
                    self._frame_bytes = jpeg

                # Grabar en el vídeo diario
                self._grabar_frame(frame)

                time.sleep(1.0 / (self.FPS_ESCRITURA * 2))  # no saturar CPU

            cap.release()
            self._cerrar_writer()
            time.sleep(3)

    # ------------------------------------------------------------------ #
    # Grabación de vídeo diario                                           #
    # ------------------------------------------------------------------ #

    def _ruta_video_hoy(self) -> Path:
        nombre = datetime.now().strftime("%Y-%m-%d") + f"_{self.id}.mp4"
        return self.directorio_videos / nombre

    def _abrir_writer(self, frame_shape: tuple) -> cv2.VideoWriter:
        h, w = frame_shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        ruta = str(self._ruta_video_hoy())
        writer = cv2.VideoWriter(ruta, fourcc, self.FPS_ESCRITURA, (w, h))
        self.logger.info(f"[{self.id}] Nuevo video diario -> {ruta}")
        return writer

    def _cerrar_writer(self) -> None:
        with self._writer_lock:
            if self._writer is not None:
                self._writer.release()
                self._writer = None
                self._fecha_grabacion = None

    def _grabar_frame(self, frame) -> None:
        hoy = date.today()
        with self._writer_lock:
            # Rotación automática a medianoche
            if self._fecha_grabacion != hoy:
                if self._writer is not None:
                    self._writer.release()
                    self._writer = None
                self._fecha_grabacion = hoy

            if self._writer is None:
                self._writer = self._abrir_writer(frame.shape)

            self._writer.write(frame)

    # ------------------------------------------------------------------ #
    # Limpieza automática                                                  #
    # ------------------------------------------------------------------ #

    def _bucle_limpieza(self) -> None:
        """Cada 24 h elimina vídeos con más de DIAS_RETENCION días."""
        while True:
            self._limpiar_videos_antiguos()
            time.sleep(86_400)

    def _limpiar_videos_antiguos(self) -> None:
        ahora  = time.time()
        limite = self.DIAS_RETENCION * 86_400

        for archivo in self.directorio_videos.glob("*.mp4"):
            if ahora - archivo.stat().st_mtime > limite:
                try:
                    archivo.unlink()
                    self.logger.info(
                        f"[{self.id}] Eliminado video antiguo: {archivo.name}"
                    )
                except OSError as e:
                    self.logger.error(
                        f"[{self.id}] Error al borrar {archivo.name}: {e}"
                    )

    # ------------------------------------------------------------------ #
    # Instantáneas                                                         #
    # ------------------------------------------------------------------ #

    def capturar_instantanea(
        self, directorio: str | Path | None = None
    ) -> Path | None:
        """
        Guarda el frame actual como JPEG.

        Returns:
            Path del archivo creado, o None si aún no hay frame.
        """
        jpeg = self.frame_bytes
        if jpeg is None:
            self.logger.warning(f"[{self.id}] Sin frame para instantanea")
            return None

        dest = Path(directorio) if directorio else (
            Path("capturas") / "snapshots" / self.id
        )
        dest.mkdir(parents=True, exist_ok=True)

        nombre = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + f"_{self.id}.jpg"
        ruta = dest / nombre
        ruta.write_bytes(jpeg)
        self.logger.info(f"[{self.id}] Instantanea -> {ruta}")
        return ruta

    # ------------------------------------------------------------------ #
    # Generador MJPEG para Flask                                          #
    # ------------------------------------------------------------------ #

    def generar_frames_mjpeg(self):
        """
        Generador compatible con:
            Flask Response(..., mimetype='multipart/x-mixed-replace; boundary=frame')

        Controla la tasa de envío a FPS_STREAM y sólo emite cuando el
        frame ha cambiado, evitando duplicados y saturación de red.
        """
        intervalo    = 1.0 / self.FPS_STREAM
        ultimo_envio = 0.0
        ultimo_jpeg: bytes | None = None

        while True:
            jpeg = self.frame_bytes

            if jpeg is None:
                time.sleep(0.05)
                continue

            ahora = time.monotonic()
            espera = intervalo - (ahora - ultimo_envio)
            if espera > 0:
                time.sleep(espera)

            if jpeg is not ultimo_jpeg:
                ultimo_jpeg  = jpeg
                ultimo_envio = time.monotonic()
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
                )

    # ------------------------------------------------------------------ #
    # Utilidades                                                           #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"<Camara id={self.id!r} ip={self.ip!r}>"

    @classmethod
    def desde_linea(cls, linea: str, logger=None) -> "Camara":
        """
        Construye una Camara desde una línea del fichero de configuración:
            id:ip:mac:port:user:password

        Para Tapo C210, port normalmente es 554.
        user/password son los de la "cuenta de cámara" de la app Tapo,
        NO los de la cuenta TP-Link.
        """
        id_cam, ip, mac, port, user, password = linea.strip().split(":")
        return cls(
            {"id": id_cam, "ip": ip, "mac": mac,
             "port": port, "user": user, "password": password},
            logger=logger,
        )