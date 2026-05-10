import os
import random
import cv2

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedLayout
from ventana_camara import VentanaCamara

# --- CONFIGURACIÓN ---
USUARIO = 'cepy01'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.60.188'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

# ---------------- CONFIGURACIÓN ----------------
SAVE_DIR = "capturas"
VIDEO_SIZE = (400, 300)
# -----------------------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

class Camara(QWidget):
    def __init__(self, id=""):
        super().__init__()
        self.id = id

        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)

        self.crear_celda()
        self.activa_camara()

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

        # Layout superpuesto
        stack = QStackedLayout()
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        stack.addWidget(self.label_video)
        stack.addWidget(self.label_titulo)

        self.setLayout(stack)

    def activa_camara(self):
        # self.cap = cv2.VideoCapture(0)
        self.cap = cv2.VideoCapture(RTSP_URL)

        if not self.cap.isOpened():
            self.label_video.setText("No se pudo abrir la cámara")
            return

        self.timer.start(30)  # ~33 FPS

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

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
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.ventana = VentanaCamara(self)
            self.ventana.show()
