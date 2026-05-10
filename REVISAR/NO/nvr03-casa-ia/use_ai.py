import cv2
import threading
import numpy as np


class CameraViewer:
    def __init__(self):
        self.cameras = [
            {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02", "user": "CEPY2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.1.39", "id": "Jardin", "user": "CEPY2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02", "user": "CEPY2026",
             "password": "Castelar2026", "port": 554},
        ]
        self.frames = [None] * len(self.cameras)
        self.locks = [threading.Lock() for _ in range(len(self.cameras))]
        self.running = True

    def get_rtsp_url(self, camera):
        return f"rtsp://{camera['user']}:{camera['password']}@{camera['ip']}:{camera['port']}/stream2"

    def camera_thread(self, index):
        cam = self.cameras[index]
        url = self.get_rtsp_url(cam)
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            print(f"Error conectando a cámara {cam['id']}")
            return

        print(f"Conectado a {cam['id']} ({cam['ip']})")

        while self.running:
            ret, frame = cap.read()
            if ret:
                with self.locks[index]:
                    self.frames[index] = frame
            else:
                print(f"Error leyendo frame de {cam['id']}")

        cap.release()

    def start(self):
        # Crear hilos para cada cámara
        threads = []
        for i in range(len(self.cameras)):
            thread = threading.Thread(target=self.camera_thread, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # Mostrar ventana con todas las cámaras
        cv2.namedWindow("CCTV System", cv2.WINDOW_NORMAL)

        while self.running:
            frames_to_show = []

            # Obtener frames actualizados
            for i in range(len(self.cameras)):
                with self.locks[i]:
                    if self.frames[i] is not None:
                        frame = self.frames[i].copy()
                        # Redimensionar y agregar texto de identificación
                        frame = cv2.resize(frame, (400, 300))
                        cv2.putText(frame, self.cameras[i]['id'], (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        frames_to_show.append(frame)

            # Organizar en cuadrícula 2x3
            # Mostrar las cámaras disponibles sin importar cuántas haya
            count = len(frames_to_show)

            if count > 0:
                # Completar hasta 6 espacios con cuadros vacíos
                while len(frames_to_show) < 6:
                    frames_to_show.append(np.zeros((300, 400, 3), dtype=np.uint8))

                top_row = np.hstack(frames_to_show[:3])
                bottom_row = np.hstack(frames_to_show[3:6])

                grid = np.vstack((top_row, bottom_row))
                cv2.imshow("CCTV System", grid)

            # Salir con ESC
            if cv2.waitKey(1) == 27:
                self.running = False
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    viewer = CameraViewer()
    viewer.start()
