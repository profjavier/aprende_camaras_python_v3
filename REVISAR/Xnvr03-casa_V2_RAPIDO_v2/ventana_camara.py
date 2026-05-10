from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class VentanaCamara(QWidget):
    def __init__(self, camara_origen):
        super().__init__()
        self.camara_origen = camara_origen

        self.setWindowTitle(f"Cámara {camara_origen.id}")
        self.resize(800, 600)

        self.label_video = QLabel()
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_video.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label_video)

        # Timer propio, pero usa el MISMO frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)

    def actualizar_frame(self):
        if self.camara_origen.label_video.pixmap():
            self.label_video.setPixmap(
                self.camara_origen.label_video.pixmap().scaled(
                    self.label_video.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
