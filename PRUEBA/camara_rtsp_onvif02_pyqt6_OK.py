'''pip install pyqt6 opencv-python onvif-zeep'''

import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

from onvif import ONVIFCamera


# ======================
# CONFIG CAMARA
# ======================
ip = '192.168.60.153'
port = 2020
user = 'cepy2026'
password = 'Castelar2026'

rtsp_url = f"rtsp://{user}:{password}@{ip}:554/stream1"


# ======================
# ONVIF PTZ
# ======================
camera = ONVIFCamera(ip, port, user, password)
media = camera.create_media_service()
ptz = camera.create_ptz_service()
profile = media.GetProfiles()[0]
token = profile.token


def move(x, y):
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = token
    request.Velocity = {
        'PanTilt': {'x': x, 'y': y},
        'Zoom': {'x': 0}
    }
    ptz.ContinuousMove(request)


def stop():
    ptz.Stop({'ProfileToken': token})


# ======================
# GUI
# ======================
class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tapo PTZ Control")

        # video
        self.label = QLabel()
        self.label.setFixedSize(640, 480)

        # botones
        self.btn_up = QPushButton("⬆ Arriba")
        self.btn_down = QPushButton("⬇ Abajo")
        self.btn_left = QPushButton("⬅ Izquierda")
        self.btn_right = QPushButton("➡ Derecha")
        self.btn_stop = QPushButton("⏹ Stop")

        # eventos
        self.btn_up.clicked.connect(lambda: self.control(0, 0.5))
        self.btn_down.clicked.connect(lambda: self.control(0, -0.5))
        self.btn_left.clicked.connect(lambda: self.control(-0.5, 0))
        self.btn_right.clicked.connect(lambda: self.control(0.5, 0))
        self.btn_stop.clicked.connect(stop)

        # layout botones
        h1 = QHBoxLayout()
        h1.addWidget(self.btn_left)
        h1.addWidget(self.btn_stop)
        h1.addWidget(self.btn_right)

        h2 = QHBoxLayout()
        h2.addWidget(self.btn_up)
        h2.addWidget(self.btn_down)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(h2)
        layout.addLayout(h1)

        self.setLayout(layout)

        # video capture
        self.cap = cv2.VideoCapture(rtsp_url)

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def control(self, x, y):
        move(x, y)

    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)

            self.label.setPixmap(QPixmap.fromImage(img))


    def closeEvent(self, event):
        self.cap.release()
        stop()
        event.accept()


# ======================
# RUN APP
# ======================
app = QApplication(sys.argv)
window = CameraApp()
window.show()
sys.exit(app.exec())