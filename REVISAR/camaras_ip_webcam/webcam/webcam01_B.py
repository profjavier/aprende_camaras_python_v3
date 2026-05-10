import sys
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cámara del portátil - PyQt6")
        self.setGeometry(200, 200, 800, 600)

        # Label para mostrar el vídeo
        self.label = QLabel(self)
        self.label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Iniciar cámara (0 = cámara por defecto)
        self.cap = cv2.VideoCapture(0)

        # Timer para actualizar frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ms

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convertir BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec())
