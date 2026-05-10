import threading
import time
import os
import datetime
import cv2
import numpy as np
import queue


class Camara:

    UNIDAD_CAPTURAS = "/home/javier/ssd"
    # Añade al video secuencias de frames
    NUM_FRAMES_TMP = 10

    def __init__(self, app):
        self.app_flask = app

        self.frames = {}
        self.locks = {}

        self.camaras_stream = {}
        self.camaras_config = []

        # snapshot / estado
        self.ultima_fecha_captura = {}

        # vídeo diario
        self.video_writer = {}
        self.video_dia_actual = {}

        self.frame_count = {}
        self.video_queues = {}


    # -------------------------
    # RTSP
    # -------------------------
    def get_rtsp(self, cam):
        return f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:{cam['port']}/Streaming/stream2"

    # -------------------------
    # CAPTURA PRINCIPAL
    # -------------------------
    def capturar_camara(self, cam):
        cam_id = cam["id"]

        while True:
            cap = cv2.VideoCapture(self.get_rtsp(cam), cv2.CAP_FFMPEG)

            if not cap.isOpened():
                self.app_flask.logger.warning(f"No conecta cámara {cam_id}")
                time.sleep(2)
                continue

            while True:
                success, frame = cap.read()

                if not success or frame is None:
                    self.app_flask.logger.warning(f"Cámara {cam_id} sin frame / caída")
                    cap.release()
                    break

                # -------------------------------------------------
                # VIDEO DIARIO
                # SOLO CADA 10 FRAMES
                # -------------------------------------------------
                try:

                    self.frame_count[cam_id] += 1

                    # escribir 1 de cada 10 frames
                    if self.frame_count[cam_id] % self.NUM_FRAMES_TMP == 0:

                        try:

                            self.frame_count[cam_id] += 1

                            if self.frame_count[cam_id] % self.NUM_FRAMES_TMP == 0:

                                if not self.video_queues[cam_id].full():

                                    self.video_queues[cam_id].put_nowait(
                                        frame.copy()
                                    )

                        except Exception as e:
                            self.app_flask.logger.error(
                                f"Error cola vídeo {cam_id}: {e}"
                            )

                except Exception as e:
                    self.app_flask.logger.error(
                        f"Error vídeo {cam_id}: {e}"
                    )

                # -------------------------
                # STREAM WEB
                # -------------------------
                try:
                    _, buffer = cv2.imencode('.jpg', frame)
                    buffer_jpeg = buffer.tobytes()

                    with self.locks[cam_id]:
                        self.frames[cam_id] = buffer_jpeg

                except Exception:
                    continue

                time.sleep(0.03)

    # -------------------------
    # VIDEO WRITER DIARIO
    # -------------------------
    '''def get_video_writer(self, cam_id, frame):
        hoy = datetime.date.today()

        # cambio de día → nuevo archivo
        if self.video_dia_actual.get(cam_id) != hoy:

            # cerrar anterior
            if cam_id in self.video_writer:
                try:
                    self.video_writer[cam_id].release()
                except:
                    pass

            base_dir = os.path.join(self.UNIDAD_CAPTURAS, "videos", cam_id)
            os.makedirs(base_dir, exist_ok=True)

            filename = hoy.strftime("%Y-%m-%d.mp4")
            ruta = os.path.join(base_dir, filename)

            height, width, _ = frame.shape

            fourcc = cv2.VideoWriter.fourcc(*'mp4v')
            # fourcc = cv2.VideoWriter.fourcc(*'MJPG')

            writer = cv2.VideoWriter(
                ruta,
                fourcc,
                10,
                (width, height)
            )

            self.video_writer[cam_id] = writer
            self.video_dia_actual[cam_id] = hoy

        return self.video_writer[cam_id]'''

    #RASPBERRY
    def get_video_writer(self, cam_id, frame):

        hoy = datetime.date.today()

        if self.video_dia_actual.get(cam_id) != hoy:

            # cerrar anterior
            if cam_id in self.video_writer:
                try:
                    self.video_writer[cam_id].release()
                except:
                    pass

            base_dir = os.path.join(
                self.UNIDAD_CAPTURAS,
                "videos",
                cam_id
            )

            os.makedirs(base_dir, exist_ok=True)

            filename = hoy.strftime("%Y-%m-%d.avi")
            ruta = os.path.join(base_dir, filename)

            height, width = frame.shape[:2]

            # MUCHO MÁS COMPATIBLE EN RPI
            #fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fourcc = cv2.VideoWriter.fourcc(*'MJPG')

            writer = cv2.VideoWriter(
                ruta,
                fourcc,
                10,
                (width, height)
            )

            # validar
            if not writer.isOpened():
                self.app_flask.logger.error(
                    f"No se pudo abrir writer: {ruta}"
                )
                return None

            self.video_writer[cam_id] = writer
            self.video_dia_actual[cam_id] = hoy

            self.app_flask.logger.info(
                f"Grabando vídeo: {ruta}"
            )

        return self.video_writer.get(cam_id)

    # -------------------------
    # STREAM FLASK
    # -------------------------
    def generar_frames(self, cam_id):
        while True:
            with self.locks.get(cam_id, threading.Lock()):
                frame = self.frames.get(cam_id)

            if frame is None:
                time.sleep(0.1)
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

    # -------------------------
    # SNAPSHOT MANUAL
    # -------------------------
    def capturar_snapshot(self, cam_id):
        with self.locks.get(cam_id, threading.Lock()):
            frame = self.frames.get(cam_id)

        if frame is None:
            return None

        base_dir = os.path.join(self.UNIDAD_CAPTURAS, "capturas", cam_id, "snapshots")
        os.makedirs(base_dir, exist_ok=True)

        fecha = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
        ruta = os.path.join(base_dir, fecha)

        img = cv2.imdecode(
            np.frombuffer(frame, np.uint8),
            cv2.IMREAD_COLOR
        )

        cv2.imwrite(ruta, img)

        return ruta

    # -------------------------
    # INICIALIZACIÓN
    # -------------------------
    def inicializar_camaras(self):

        for cam in self.camaras_config:
            cam_id = cam["id"]
            self.frame_count[cam_id] = 0
            self.video_queues[cam_id] = queue.Queue(maxsize=20)
            self.frames[cam_id] = None
            self.locks[cam_id] = threading.Lock()

            self.ultima_fecha_captura[cam_id] = None
            self.video_dia_actual[cam_id] = None

            t = threading.Thread(
                target=self.capturar_camara,
                args=(cam,),
                daemon=True
            )
            t.start()

            t_video = threading.Thread(
                target=self.grabador_video,
                args=(cam_id,),
                daemon=True
            )

            t_video.start()

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

    def grabador_video(self, cam_id):
        self.app_flask.logger.info(
            f"Grabador iniciado {cam_id}"
        )
        while True:

            try:
                frame = self.video_queues[cam_id].get()
                self.app_flask.logger.info(
                    f"Frame recibido grabador {cam_id}"
                )
                if frame is None:
                    continue

                writer = self.get_video_writer(
                    cam_id,
                    frame
                )

                if writer is not None:
                    writer.write(frame)

            except Exception as e:
                self.app_flask.logger.error(
                    f"Error grabador {cam_id}: {e}"
                )