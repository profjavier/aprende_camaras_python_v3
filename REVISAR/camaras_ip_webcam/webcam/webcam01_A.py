import sys
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camara del portatil - PyQt6")
        self.resize(800, 600)

        # UI
        self.label = QLabel("Cargando camara...")
        self.label.setScaledContents(True)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # OpenCV camera
        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~33 FPS

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec())
