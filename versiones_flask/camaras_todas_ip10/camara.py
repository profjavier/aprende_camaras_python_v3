import threading
import time
import os
import datetime
import cv2
import numpy as np

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp|"
    "stimeout;3000000|"
    "fflags;nobuffer|"
    "flags;low_delay"
)


class Camara:

    UNIDAD_CAPTURAS = "/home/javier/ssd"
    TIEMPO_INACTIVIDAD = 30

    def __init__(self, app):
        self.app_flask = app

        self.frames = {}
        self.locks = {}
        self.camaras_activas = []

        self.capture_threads = {}
        self.stop_flags = {}

        # 🔴 CONTROL GLOBAL POR PING
        self.last_ping = time.time()
        self.captura_activa = False
        self.estado_lock = threading.Lock()

        self.watchdog_started = False

    # -------------------------
    # PING (LO ACTUALIZA EL ENDPOINT)
    # -------------------------
    def ping(self):
        with self.estado_lock:
            self.last_ping = time.time()
            if not self.captura_activa:
                print("🟢 ping recibido → activando sistema")
                self.captura_activa = True

    # -------------------------
    # WATCHDOG GLOBAL
    # -------------------------
    def watchdog(self):
        while True:
            time.sleep(2)

            with self.estado_lock:
                inactivo = (time.time() - self.last_ping) > self.TIEMPO_INACTIVIDAD

                if inactivo and self.captura_activa:
                    print("🔴 inactividad → apagando TODO RTSP")
                    self.captura_activa = False

                elif not inactivo and not self.captura_activa:
                    print("🟢 actividad → reactivando sistema")
                    self.captura_activa = True

    # -------------------------
    # RTSP LOOP
    # -------------------------
    def capturar_camara(self, cam):

        cam_id = cam["id"]
        cap = None

        while True:

            # 🔴 BLOQUEO GLOBAL
            if not self.captura_activa:
                if cap:
                    print(f"🛑 cerrando RTSP {cam_id}")
                    cap.release()
                    cap = None

                time.sleep(1)
                continue

            # 🔴 abrir conexión solo si hace falta
            if cap is None:
                print(f"📡 abriendo RTSP {cam_id}")
                cap = cv2.VideoCapture(self.get_rtsp(cam), cv2.CAP_FFMPEG)

                if not cap.isOpened():
                    print("❌ error RTSP")
                    cap = None
                    time.sleep(2)
                    continue

            success, frame = cap.read()

            if not success:
                print("⚠️ reconectando RTSP")
                cap.release()
                cap = None
                continue

            _, buffer = cv2.imencode(".jpg", frame)

            with self.locks[cam_id]:
                self.frames[cam_id] = buffer.tobytes()

    # -------------------------
    # STREAM FLASK
    # -------------------------
    def generar_frames(self, cam_id):

        cam = next(c for c in self.camaras_activas if c["id"] == cam_id)

        # self.ping()

        self.start_capture_if_needed(cam)

        try:
            while True:

                # self.ping()

                with self.locks[cam_id]:
                    frame = self.frames.get(cam_id)

                if frame is None:
                    time.sleep(0.1)
                    continue

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame +
                    b'\r\n'
                )

        except GeneratorExit:
            print("👋 cliente desconectado")

    # -------------------------
    # INIT
    # -------------------------
    def inicializar_camaras(self):

        for cam in self.camaras_activas:
            cam_id = cam["id"]

            self.frames[cam_id] = None
            self.locks[cam_id] = threading.Lock()
            self.stop_flags[cam_id] = False

        if not self.watchdog_started:
            threading.Thread(
                target=self.watchdog,
                daemon=True
            ).start()

            self.watchdog_started = True

    # -------------------------
    # START CAMARA
    # -------------------------
    def start_capture_if_needed(self, cam):

        cam_id = cam["id"]

        if cam_id in self.capture_threads:
            return

        t = threading.Thread(
            target=self.capturar_camara,
            args=(cam,),
            daemon=True
        )

        t.start()
        self.capture_threads[cam_id] = t

    # -------------------------
    # RTSP URL
    # -------------------------
    def get_rtsp(self, cam):
        return f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:{cam['port']}/Streaming/stream2"


    # -------------------------
    # CONFIG CAMARAS
    # -------------------------
    def cargar_camaras(self, ruta):

        camaras = []

        self.app_flask.logger.info(f"Cargando cámaras desde {ruta}")

        try:
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

            self.app_flask.logger.info("Cámaras cargadas")

        except Exception:
            self.app_flask.logger.exception("Error cargando cámaras")

        return camaras
