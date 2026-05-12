# webcam.py
import cv2


class Webcam:
    def __init__(self):
        self.camara = None
        self.camara_iniciada = False

    def iniciar(self, id=0):
        # CAPTURA DE CÁMARA WEB
        # 0 = cámara por defecto del sistema (id)
        self.camara = cv2.VideoCapture( id )
        self.camara_iniciada = True

    # GENERADOR DE FRAMES (STREAMING)
    def generar_frames(self):
        while True:
            # Captura un frame desde la cámara
            success, frame = self.camara.read()

            # Si falla la cámara, se detiene el bucle
            if not success:
                break
            else:
                # ---------------------------
                # CONVERSIÓN DE IMAGEN
                # ---------------------------
                # Convierte el frame (matriz OpenCV) a formato JPEG comprimido
                ret, buffer = cv2.imencode('.jpg', frame)

                # Convierte la imagen a bytes (formato enviable por HTTP)
                frame = buffer.tobytes()

                # ---------------------------
                # STREAMING CON YIELD
                # ---------------------------
                # En lugar de devolver todo de golpe,
                # yield envía cada frame uno a uno al navegador
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')