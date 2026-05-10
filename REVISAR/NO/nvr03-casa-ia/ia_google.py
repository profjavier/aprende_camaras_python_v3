import cv2
import threading
import numpy as np


class CamaraIP:
    def __init__(self, config):
        self.id = config['id']
        # El formato RTSP varía según la marca (ej: /live, /h264, etc.)
        # Ajusta '/live' según el manual de tu cámara
        self.url = f"rtsp://{config['user']}:{config['password']}@{config['ip']}:{config['port']}/stream2"
        self.cap = cv2.VideoCapture(self.url)
        self.frame = None
        self.ret = False
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                continue
            self.ret, self.frame = self.cap.read()

    def stop(self):
        self.stopped = True
        self.cap.release()


class AppVCR:
    def __init__(self, lista_config):
        # Inicializamos hilos para cada cámara
        self.camaras = [CamaraIP(c).start() for c in lista_config]

    def run(self):
        while True:
            frames = []
            for cam in self.camaras:
                if cam.frame is not None:
                    # Redimensionamos para que quepan en el mosaico (ej: 400x300)
                    f = cv2.resize(cam.frame, (400, 300))
                    cv2.putText(f, cam.id, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    frames.append(f)
                else:
                    # Frame negro si la cámara no carga
                    frames.append(np.zeros((300, 400, 3), dtype=np.uint8))

            # Crear mosaico: 2 filas (3 arriba, 2 abajo + 1 vacío)
            fila1 = np.hstack(frames[:3])
            # La fila 2 necesita un relleno si solo hay 5 cámaras
            relleno = np.zeros((300, 400, 3), dtype=np.uint8)
            fila2 = np.hstack(frames[3:] + [relleno])

            mosaico = np.vstack([fila1, fila2])

            cv2.imshow("VCR Multipantalla - 5 Cámaras", mosaico)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        for cam in self.camaras:
            cam.stop()
        cv2.destroyAllWindows()


# Tu configuración
config_camaras = [
    {"mac": "ec:75:0c:12:2f:83", "ip": "192.168.1.200", "id": "casa", "user": "javier", "password": "castelar2026",
     "port": 554},
    {"mac": "50:3d:d1:b8:e9:f4", "ip": "192.168.1.129", "id": "cepy02", "user": "cepy2026", "password": "castelar2026",
     "port": 554},
    {"mac": "50:3d:d1:b8:db:cf", "ip": "192.168.1.39", "id": "jardin", "user": "cepy2026", "password": "castelar2026",
     "port": 554},
    {"mac": "ec:75:0c:12:2f:83", "ip": "192.168.1.200", "id": "casa_alt", "user": "javier", "password": "castelar2026",
     "port": 554},
    {"mac": "50:3d:d1:b8:e9:f4", "ip": "192.168.1.129", "id": "cepy02_alt", "user": "cepy2026",
     "password": "castelar2026", "port": 554},
]

if __name__ == "__main__":
    app = AppVCR(config_camaras)
    app.run()