# pip install python-vlc PyQt6


import sys
import vlc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout
)
from PyQt6.QtCore import Qt


class CameraWidget(QFrame):
    def __init__(self, camera):
        super().__init__()

        self.camera = camera
        self.instance = vlc.Instance(
            "--no-audio",
            "--rtsp-tcp",
            "--network-caching=300",
            "--file-caching=300",
            "--avcodec-hw=dxva2",
        )

        self.player = self.instance.media_player_new()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.label = QLabel(camera["id"])
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color:white; background:#222; padding:4px;")

        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background:black;")

        layout.addWidget(self.label)
        layout.addWidget(self.video_frame)

        self.player.set_hwnd(int(self.video_frame.winId()))

        rtsp_url = (
            f"rtsp://{camera['user']}:{camera['password']}"
            f"@{camera['ip']}:{camera['port']}/stream2"
        )

        media = self.instance.media_new(rtsp_url)
        media.add_option(":rtsp-tcp")
        media.add_option(":network-caching=300")
        self.player.set_media(media)
        self.player.play()


class NVRWindow(QWidget):
    def __init__(self, cameras):
        super().__init__()

        self.setWindowTitle("NVR – Cámaras IP")
        self.setStyleSheet("background:black;")
        self.showMaximized()

        grid = QGridLayout(self)
        grid.setSpacing(4)

        cols = 2  # Ajusta si quieres 3 o 4 columnas
        row = col = 0

        for cam in cameras:
            widget = CameraWidget(cam)
            grid.addWidget(widget, row, col)

            col += 1
            if col >= cols:
                col = 0
                row += 1


if __name__ == "__main__":
    cameras = [
        {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa",
         "user": "javier", "password": "Castelar2026", "port": 554},

        {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02",
         "user": "CEPY2026", "password": "Castelar2026", "port": 554},

        {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.1.39", "id": "Jardin",
         "user": "CEPY2026", "password": "Castelar2026", "port": 554},

        # {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa 2",
        #  "user": "javier", "password": "Castelar2026", "port": 554},
        #
        # {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02 2",
        #  "user": "CEPY2026", "password": "Castelar2026", "port": 554},
    ]

    app = QApplication(sys.argv)
    win = NVRWindow(cameras)
    win.show()
    sys.exit(app.exec())
