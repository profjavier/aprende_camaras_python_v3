import os
import time
import threading
import cv2
from datetime import datetime, timedelta


class CamaraStream:
    def __init__(self, logger=None, base_dir="camaras"):
        self.logger = logger
        self.base_dir = base_dir

        self.camaras_config = []
        self.frames = {}
        self.locks = {}

        os.makedirs(self.base_dir, exist_ok=True)

    # -------------------------
    # INICIALIZACIÓN
    # -------------------------
    def inicializar(self, ruta_config):
        self.camaras_config = self._cargar_camaras(ruta_config)

        self._iniciar_streams()
        self._iniciar_limpieza()

    # -------------------------
    # ARRANQUE DE HILOS
    # -------------------------
    def _iniciar_streams(self):
        for cam in self.camaras_config:
            cam_id = cam["id"]

            self.frames[cam_id] = None
            self.locks[cam_id] = threading.Lock()

            t = threading.Thread(
                target=self._capturar_camara,
                args=(cam,),
                daemon=True
            )
            t.start()

    def _iniciar_limpieza(self):
        t = threading.Thread(
            target=self._limpiar_antiguos,
            daemon=True
        )
        t.start()

    # -------------------------
    # CAPTURA + GRABACIÓN
    # -------------------------
    def _capturar_camara(self, cam):
        cam_id = cam["id"]

        cap = cv2.VideoCapture(self._get_rtsp(cam), cv2.CAP_FFMPEG)

        if not cap.isOpened():
            self._log(f"No conecta cámara {cam_id}")
            return

        writer = self._crear_writer(cam)
        last_day = datetime.now().date()

        while True:
            success, frame = cap.read()

            if not success:
                time.sleep(2)
                continue

            # STREAM WEB
            _, buffer = cv2.imencode('.jpg', frame)
            frame_jpg = buffer.tobytes()

            with self.locks[cam_id]:
                self.frames[cam_id] = frame_jpg

            # GRABACIÓN DIARIA
            today = datetime.now().date()

            if today != last_day:
                writer.release()
                writer = self._crear_writer(cam)
                last_day = today

            writer.write(frame)

            time.sleep(0.03)

    # -------------------------
    # STREAM FLASK
    # -------------------------
    def generar_frames(self, cam_id):
        while True:
            with self.locks[cam_id]:
                frame = self.frames.get(cam_id)

            if frame is None:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

    def get_camaras(self):
        return self.camaras_config
    # -------------------------
    # RTSP
    # -------------------------
    def _get_rtsp(self, cam):
        return f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:{cam['port']}/Streaming/stream2"


    # -------------------------
    # GRABACIÓN
    # -------------------------
    def _crear_writer(self, cam):
        cam_dir = os.path.join(self.base_dir, cam["id"])
        os.makedirs(cam_dir, exist_ok=True)

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.avi")
        path = os.path.join(cam_dir, filename)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 20
        size = (640, 480)

        return cv2.VideoWriter(path, fourcc, fps, size)

    # -------------------------
    # LIMPIEZA (7 DÍAS)
    # -------------------------
    def _limpiar_antiguos(self):
        while True:
            cutoff = datetime.now() - timedelta(days=7)

            for cam in self.camaras_config:
                cam_dir = os.path.join(self.base_dir, cam["id"])

                if not os.path.exists(cam_dir):
                    continue

                for file in os.listdir(cam_dir):
                    path = os.path.join(cam_dir, file)

                    try:
                        if os.path.isfile(path):
                            mtime = datetime.fromtimestamp(os.path.getmtime(path))

                            if mtime < cutoff:
                                os.remove(path)
                    except Exception as e:
                        self._log(f"Error borrando {path}: {e}")

            time.sleep(3600)

    # -------------------------
    # CONFIG
    # -------------------------
    def _cargar_camaras(self, ruta):
        camaras = []

        with open(ruta, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue

                id_cam, ip, mac, port, user, password = linea.split(":")

                camaras.append({
                    "id": id_cam,
                    "ip": ip,
                    "mac": mac,
                    "port": int(port),
                    "user": user,
                    "password": password
                })

        return camaras

    # -------------------------
    # LOG
    # -------------------------
    def _log(self, msg):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)