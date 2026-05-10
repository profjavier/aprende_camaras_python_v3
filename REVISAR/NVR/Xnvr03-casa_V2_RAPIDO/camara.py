import random
import cv2

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedLayout
from ventana_camara import VentanaCamara
from video_thread import VideoThread

class Camara(QWidget):
    def __init__(self, id, user, password, ip, port):
        super().__init__()
        self.id = id
        self.user = user
        self.password = password
        self.ip = ip
        self.port = port
        self.rtsp_url = f"rtsp://{self.user}:{self.password}@{self.ip}:{self.port}/stream1"

        self.crear_celda()

        # Hilo de video
        self.video_thread = VideoThread(self.rtsp_url)
        self.video_thread.frame_ready.connect(self.mostrar_frame)
        self.video_thread.start()

    def crear_celda(self):
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgb({r},{g},{b});
                border-radius: 8px;
            }}
        """)

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

        stack = QStackedLayout()
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        stack.addWidget(self.label_video)
        stack.addWidget(self.label_titulo)
        self.setLayout(stack)

    def mostrar_frame(self, frame):
        # Reducir tamaño al tamaño del QLabel para renderizar rápido
        w, h = self.label_video.width(), self.label_video.height()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (w, h))
        qimg = QImage(frame.data, w, h, 3*w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        if hasattr(self, "video_thread"):
            self.video_thread.stop()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.ventana = VentanaCamara(self)
            self.ventana.show()
