from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from PyQt6.QtGui import QIcon
import datetime
import os
import random
import cv2

from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedLayout
from ventana_camara import VentanaCamara
from hilo_camara import HiloCamara

class Camara(QWidget):
    def __init__(self, id, user,password, ip, port):
        super().__init__()
        self.id = id
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port

        self.rtsp_url = f"rtsp://{self.user}:{self.password}@{self.ip}:{self.port}/stream2"


        self.cap = None

        self.grabando = False
        self.video_writer = None
        self.ultimo_frame = None

        # Carpeta donde se guardarán archivos
        self.carpeta_guardado = "capturas"
        os.makedirs(self.carpeta_guardado, exist_ok=True)

        self.crear_celda()
        # self.activa_camara()

    def crear_celda(self):
        # Color aleatorio
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        '''self.setStyleSheet("""
            QWidget {
                background-color: black;
                border-radius: 12px;
            }
        """)'''
        self.setStyleSheet(
            f"""
                    QWidget {{
                        background-color: rgb({r},{g},{b});
                        border-radius: 8px;
                    }}
                    """
        )

        self.label_video = QLabel()
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_video.setStyleSheet("background: transparent;")

        self.label_titulo = QLabel(f"Cámara {self.id}")
        self.label_titulo.setStyleSheet("""
            color: white;
            font-size: 10px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 120);
            padding: 2px 6px;
        """)
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Botón de foto
        self.btn_foto = QPushButton()
        self.btn_foto.setIcon(QIcon("icons/camera.svg"))
        self.btn_foto.setToolTip("Tomar foto")
        self.btn_foto.clicked.connect(self.guardar_foto)

        # Botón de grabar video
        self.btn_video = QPushButton()
        self.btn_video.setIcon(QIcon("icons/video.svg"))
        self.btn_video.setToolTip("Grabar video")
        self.btn_video.clicked.connect(self.toggle_video)

        # Barra horizontal para botones
        barra_botones = QHBoxLayout()
        barra_botones.addWidget(self.btn_foto)
        barra_botones.addWidget(self.btn_video)
        barra_botones.setAlignment(Qt.AlignmentFlag.AlignRight)

        contenedor = QWidget()
        contenedor.setLayout(barra_botones)
        contenedor.setStyleSheet("background: transparent;")

        # Layout superpuesto
        stack = QStackedLayout()
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        stack.addWidget(self.label_video)
        stack.addWidget(self.label_titulo)
        stack.addWidget(contenedor)

        self.setLayout(stack)

    # def activa_camara(self):
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.actualizar_frame)
    #     self.cap = cv2.VideoCapture(self.rtsp_url)
    #
    #     if not self.cap.isOpened():
    #         self.label_video.setText("No se pudo abrir la cámara")
    #         return
    #
    #     self.timer.start(15)  # ~33 FPS

    def activa_camara(self):
        # Arrancar en un hilo para no bloquear la UI
        self.thread = QThread()
        self.worker = HiloCamara(self)

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.conexion_lista)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Guardamos el frame original para foto y video
        self.ultimo_frame = frame.copy()

        # Si estamos grabando, guardar frame en video
        if self.grabando and self.video_writer is not None:
            self.video_writer.write(frame)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qimg = QImage(
            frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qimg)
        self.label_video.setPixmap(
            pixmap.scaled(
                self.label_video.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()

        if self.video_writer:
            self.video_writer.release()

        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.ventana = VentanaCamara(self)
            self.ventana.show()


    def guardar_foto(self):
        if self.ultimo_frame is None:
            return

        nombre = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        ruta = os.path.join(self.carpeta_guardado, f"foto_{nombre}")

        cv2.imwrite(ruta, self.ultimo_frame)
        print(f"Foto guardada en: {ruta}")

    def toggle_video(self):
        if not self.grabando:
            # Iniciar grabación
            nombre = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
            ruta = os.path.join(self.carpeta_guardado, f"video_{nombre}")

            h, w, _ = self.ultimo_frame.shape if self.ultimo_frame is not None else (480, 640, 3)

            self.video_writer = cv2.VideoWriter(
                ruta,
                cv2.VideoWriter_fourcc(*'XVID'),
                20.0,
                (w, h)
            )

            self.grabando = True
            self.btn_video.setStyleSheet("background-color: red;")
            print("Grabación iniciada")

        else:
            # Detener grabación
            self.grabando = False
            self.btn_video.setStyleSheet("")
            self.video_writer.release()
            self.video_writer = None
            print("Grabación detenida")

    def iniciar_conexion(self):
        # Esto se ejecuta en segundo plano
        self.cap = cv2.VideoCapture(self.rtsp_url)

    def conexion_lista(self, ok):
        if self.cap is None or not self.cap.isOpened():
            self.label_video.setText("No se pudo abrir la cámara")
            return

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        #self.timer.start(15)
        self.timer.start(100)
