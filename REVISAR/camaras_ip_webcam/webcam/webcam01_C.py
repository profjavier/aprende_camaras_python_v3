import sys
import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap


class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visor de Cámara con PyQt6")
        self.resize(800, 600)

        # Widget central y layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Etiqueta para mostrar el video
        self.video_label = QLabel("Iniciando cámara...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_label)

        # Inicializar OpenCV
        self.capture = cv2.VideoCapture(0)  # 0 es la cámara por defecto

        # Configurar el Timer para actualizar los frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Aproximadamente 30 FPS

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # Convertir el frame de BGR (OpenCV) a RGB (Qt)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Obtener dimensiones
            height, width, channel = frame.shape
            bytes_per_line = channel * width

            # Crear QImage
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            # Mostrar en el QLabel
            self.video_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                self.video_label.width(),
                self.video_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))

    def closeEvent(self, event):
        # Liberar la cámara al cerrar la ventana
        self.capture.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec())