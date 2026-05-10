import cv2
import threading
import time
import numpy as np
from queue import Queue
import requests
from datetime import datetime


class CCTVViewer:
    def __init__(self, camaras):
        self.camaras = camaras
        self.streams = []
        self.frames = {}
        self.running = False
        self.threads = []
        self.frame_queue = Queue(maxsize=10)

    def build_rtsp_url(self, camara):
        """Construye la URL RTSP para la cámara"""
        return f"rtsp://{camara['user']}:{camara['password']}@{camara['ip']}:{camara['port']}/stream1"

    def check_camera_online(self, ip):
        """Verifica si la cámara está online (opcional)"""
        try:
            response = requests.get(f"http://{ip}", timeout=2)
            return response.status_code == 200
        except:
            return False

    def camera_stream(self, camara, index):
        """Hilo para capturar el stream de una cámara individual"""
        rtsp_url = self.build_rtsp_url(camara)
        print(f"Iniciando cámara {camara['id']}: {rtsp_url}")

        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while self.running:
            try:
                ret, frame = cap.read()
                if ret:
                    # Reducir tamaño para mejor rendimiento
                    frame = cv2.resize(frame, (640, 360))

                    # Añadir texto con identificador
                    cv2.putText(frame, f"{camara['id']} - {camara['ip']}",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2)

                    # Añadir timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, timestamp,
                                (10, frame.shape[0] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 255), 1)

                    self.frames[index] = frame

                else:
                    # Frame vacío - reconectar
                    print(f"Reconectando cámara {camara['id']}...")
                    cap.release()
                    time.sleep(2)
                    cap = cv2.VideoCapture(rtsp_url)

            except Exception as e:
                print(f"Error en cámara {camara['id']}: {e}")
                time.sleep(2)

        cap.release()
        print(f"Cámara {camara['id']} detenida")

    def create_layout(self):
        """Crea un layout 2x3 para las 5 cámaras (última vacía)"""
        if len(self.frames) < 5:
            return None

        # Crear una lista de frames en orden
        frame_list = []
        for i in range(5):
            if i in self.frames:
                frame_list.append(self.frames[i])
            else:
                # Frame negro si no hay conexión
                frame_list.append(np.zeros((360, 640, 3), dtype=np.uint8))

        # Crear layout 2x3
        # Primera fila: 3 cámaras
        row1 = np.hstack([frame_list[0], frame_list[1], frame_list[2]])

        # Segunda fila: 2 cámaras y espacio vacío
        empty_frame = np.zeros((360, 640, 3), dtype=np.uint8)
        cv2.putText(empty_frame, "VACIO", (250, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        row2 = np.hstack([frame_list[3], frame_list[4], empty_frame])

        # Combinar filas
        layout = np.vstack([row1, row2])

        return layout

    def start(self):
        """Inicia todas las cámaras"""
        print("Iniciando sistema de vigilancia...")
        self.running = True

        # Verificar cámaras online
        print("Verificando conexión de cámaras...")
        for i, camara in enumerate(self.camaras[:5]):  # Solo las primeras 5
            if self.check_camera_online(camara['ip']):
                print(f"Cámara {camara['id']} ({camara['ip']}): ONLINE")
            else:
                print(f"Cámara {camara['id']} ({camara['ip']}): OFFLINE")

        # Iniciar hilos para cada cámara
        for i, camara in enumerate(self.camaras[:5]):  # Solo las primeras 5
            thread = threading.Thread(target=self.camera_stream, args=(camara, i))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        # Esperar a que las cámaras inicialicen
        time.sleep(3)

        print("\nControles:")
        print("- Presiona 'ESC' para salir")
        print("- Presiona 's' para capturar pantalla")
        print("- Presiona 'r' para reiniciar cámaras")
        print("- Presiona '+' para aumentar brillo")
        print("- Presiona '-' para disminuir brillo")
        print("\nIniciando visualización...")

    def stop(self):
        """Detiene todas las cámaras"""
        print("\nDeteniendo sistema de vigilancia...")
        self.running = False

        # Esperar a que los hilos terminen
        for thread in self.threads:
            thread.join(timeout=2)

        cv2.destroyAllWindows()
        print("Sistema detenido correctamente")

    def run(self):
        """Bucle principal de visualización"""
        self.start()

        brightness = 0

        try:
            while self.running:
                if len(self.frames) >= 5:
                    layout = self.create_layout()

                    if layout is not None:
                        # Aplicar ajuste de brillo si es necesario
                        if brightness != 0:
                            hsv = cv2.cvtColor(layout, cv2.COLOR_BGR2HSV)
                            h, s, v = cv2.split(hsv)
                            v = cv2.add(v, brightness)
                            v = np.clip(v, 0, 255)
                            final_hsv = cv2.merge([h, s, v])
                            layout = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

                        # Mostrar layout
                        cv2.imshow('Sistema de Vigilancia - 5 Camaras', layout)

                        # Controles de teclado
                        key = cv2.waitKey(1) & 0xFF

                        if key == 27:  # ESC
                            break
                        elif key == ord('s'):  # Capturar pantalla
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"captura_{timestamp}.jpg"
                            cv2.imwrite(filename, layout)
                            print(f"Captura guardada como {filename}")
                        elif key == ord('r'):  # Reiniciar
                            print("Reiniciando visualización...")
                            self.frames.clear()
                            time.sleep(1)
                        elif key == ord('+'):  # Aumentar brillo
                            brightness = min(brightness + 10, 100)
                            print(f"Brillo: {brightness}")
                        elif key == ord('-'):  # Disminuir brillo
                            brightness = max(brightness - 10, -100)
                            print(f"Brillo: {brightness}")

                else:
                    # Pantalla de espera
                    wait_screen = np.zeros((720, 1920, 3), dtype=np.uint8)
                    cv2.putText(wait_screen, "Conectando con camaras...",
                                (500, 360), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)

                    connected = len(self.frames)
                    cv2.putText(wait_screen, f"Conectadas: {connected}/5",
                                (600, 400), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 255), 2)

                    cv2.imshow('Sistema de Vigilancia - 5 Camaras', wait_screen)

                    if cv2.waitKey(1) & 0xFF == 27:
                        break

        except KeyboardInterrupt:
            print("\nInterrupción por teclado")
        finally:
            self.stop()


def main():
    # Configuración de cámaras
    camaras = [
        {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa",
         "user": "javier", "password": "Castelar2026", "port": 554},
        {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02",
         "user": "CEPY2026", "password": "Castelar2026", "port": 554},
        {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.1.39", "id": "Jardin",
         "user": "CEPY2026", "password": "Castelar2026", "port": 554},
        {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa",
         "user": "javier", "password": "Castelar2026", "port": 554},
        {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02",
         "user": "CEPY2026", "password": "Castelar2026", "port": 554},
    ]

    # Nota: Hay cámaras duplicadas en la lista
    print("=" * 60)
    print("SISTEMA DE VIGILANCIA - 5 CÁMARAS IP")
    print("=" * 60)
    print("\nCámaras configuradas:")
    for i, cam in enumerate(camaras[:5], 1):
        print(f"{i}. {cam['id']} - {cam['ip']} (MAC: {cam['mac'][:8]}...)")

    print("\nNOTA: Hay direcciones IP duplicadas en la configuración.")
    print("Asegúrate de que cada cámara tenga una IP única.\n")

    # Crear y ejecutar el visor
    viewer = CCTVViewer(camaras)
    viewer.run()


if __name__ == "__main__":
    # Instalación de dependencias requeridas:
    # pip install opencv-python numpy requests

    main()