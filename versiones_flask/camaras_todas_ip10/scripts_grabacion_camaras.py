import cv2
import threading
import queue
import os
import time
import datetime


class GrabadorCamaras:

    BASE_DIR = "/home/javier/ssd/videos"

    CONFIG_FILE = "config/config_camaras.cfg"

    # guardar 1 frame cada N
    SKIP_FRAMES = 10  # Se guarda un frame de cada 10

    def __init__(self):

        self.camaras = self.cargar_camaras()

        self.video_queues = {}
        self.video_writers = {}
        self.video_day = {}
        self.frame_count = {}
        self.fps = 5  # Frames por segundo

    # ---------------------------------------------------
    # CARGAR CAMARAS DESDE CFG
    # ---------------------------------------------------
    def cargar_camaras(self):

        camaras = []

        try:

            with open(self.CONFIG_FILE, "r") as f:

                for linea in f:

                    linea = linea.strip()

                    if not linea:
                        continue

                    partes = linea.split(":")

                    if len(partes) != 6:
                        print(f"[ERROR] Línea inválida: {linea}")
                        continue

                    (
                        cam_id,
                        ip,
                        mac,
                        port,
                        user,
                        password
                    ) = partes

                    camaras.append({
                        "id": cam_id,
                        "ip": ip,
                        "mac": mac,
                        "port": int(port),
                        "user": user,
                        "password": password
                    })

            print(f"[INFO] Cámaras cargadas: {len(camaras)}")

        except Exception as e:

            print(f"[ERROR] No se pudo leer config: {e}")

        return camaras

    # ---------------------------------------------------
    # RTSP
    # ---------------------------------------------------
    def get_rtsp(self, cam):

        return (
            f"rtsp://{cam['user']}:{cam['password']}"
            f"@{cam['ip']}:{cam['port']}"
            f"/Streaming/stream2"
        )

    # ---------------------------------------------------
    # VIDEO WRITER
    # ---------------------------------------------------
    def get_video_writer(self, cam_id, frame):

        hoy = datetime.date.today()

        if self.video_day.get(cam_id) != hoy:

            # cerrar anterior
            if cam_id in self.video_writers:

                try:
                    self.video_writers[cam_id].release()
                except:
                    pass

            carpeta = os.path.join(
                self.BASE_DIR,
                cam_id
            )

            os.makedirs(carpeta, exist_ok=True)

            # nombre = hoy.strftime("%Y-%m-%d.avi") # Para AVI
            nombre = hoy.strftime("%Y-%m-%d.mp4") # para MP4

            ruta = os.path.join(
                carpeta,
                nombre
            )

            height, width = frame.shape[:2]

            # fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Para AVI
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Para MP4

            writer = cv2.VideoWriter(
                ruta,
                fourcc,
                self.fps,
                (width, height)
            )

            if not writer.isOpened():

                print(f"[ERROR] No se pudo abrir {ruta}")

                return None

            self.video_writers[cam_id] = writer
            self.video_day[cam_id] = hoy

            print(f"[INFO] Grabando {ruta}")

        return self.video_writers.get(cam_id)

    # ---------------------------------------------------
    # CAPTURA CAMARA
    # ---------------------------------------------------
    def capturar_camara(self, cam):

        cam_id = cam["id"]

        while True:

            print(f"[INFO] Conectando {cam_id}")

            cap = cv2.VideoCapture(
                self.get_rtsp(cam),
                cv2.CAP_FFMPEG
            )

            if not cap.isOpened():

                print(f"[ERROR] No conecta {cam_id}")

                time.sleep(5)

                continue

            print(f"[INFO] Cámara OK {cam_id}")

            while True:
                try:
                    success, frame = cap.read()

                    if not success or frame is None:
                        print(f"[ERROR] Cámara caída {cam_id}")
                        cap.release()
                        break

                    if cam_id not in self.frame_count:
                        self.frame_count[cam_id] = 0

                    self.frame_count[cam_id] += 1

                    if self.frame_count[cam_id] % self.SKIP_FRAMES == 0:

                        if cam_id in self.video_queues and not self.video_queues[cam_id].full():
                            self.video_queues[cam_id].put_nowait(frame.copy())

                except Exception as e:
                    print(f"[ERROR crítico cámara {cam_id}: {e}")
                    time.sleep(1)

    # ---------------------------------------------------
    # HILO GRABADOR
    # ---------------------------------------------------
    def grabador_video(self, cam_id):

        print(f"[INFO] Grabador iniciado {cam_id}")

        while True:

            try:

                frame = self.video_queues[cam_id].get()

                if frame is None:
                    continue

                writer = self.get_video_writer(
                    cam_id,
                    frame
                )

                if writer is not None:

                    writer.write(frame)

            except Exception as e:

                print(f"[ERROR] Grabador {cam_id}: {e}")

    def limpiar_videos_antiguos(self):

        limite_dias = 7
        ahora = datetime.datetime.now()

        base = self.BASE_DIR

        for cam_id in os.listdir(base):

            carpeta_cam = os.path.join(base, cam_id)

            if not os.path.isdir(carpeta_cam):
                continue

            for archivo in os.listdir(carpeta_cam):

                ruta = os.path.join(carpeta_cam, archivo)

                try:
                    if not os.path.isfile(ruta):
                        continue

                    # fecha de modificación del archivo
                    mod_time = datetime.datetime.fromtimestamp(
                        os.path.getmtime(ruta)
                    )

                    if (ahora - mod_time).days > limite_dias:
                        os.remove(ruta)

                        print(f"[INFO] Eliminado: {ruta}")

                except Exception as e:

                    print(f"[ERROR] borrando {ruta}: {e}")

    def _loop_limpieza(self):

        while True:

            try:
                self.limpiar_videos_antiguos()

            except Exception as e:
                print(f"[ERROR limpieza]: {e}")

            # cada 6 horas
            time.sleep(6 * 60 * 60)

    # ---------------------------------------------------
    # INICIAR
    # ---------------------------------------------------
    def iniciar(self):

        # ELimina los videos d mas de una semana
        t_clean = threading.Thread(
            target=self._loop_limpieza,
            daemon=True
        )

        t_clean.start()



        if not self.camaras:
            print("[ERROR] No hay cámaras")
            return

        # 🔥 PREINICIALIZAR TODO
        for cam in self.camaras:
            cam_id = cam["id"]

            self.video_queues[cam_id] = queue.Queue(maxsize=100)
            self.frame_count[cam_id] = 0
            self.video_writers[cam_id] = None
            self.video_day[cam_id] = None

        # 🔥 AHORA arrancar threads
        for cam in self.camaras:
            cam_id = cam["id"]

            t1 = threading.Thread(
                target=self.capturar_camara,
                args=(cam,),
                daemon=True
            )

            t2 = threading.Thread(
                target=self.grabador_video,
                args=(cam_id,),
                daemon=True
            )

            t1.start()
            t2.start()

        print("[INFO] Sistema iniciado")

        while True:
            time.sleep(1)





# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":

    sistema = GrabadorCamaras()

    sistema.iniciar()