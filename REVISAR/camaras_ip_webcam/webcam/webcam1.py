import sys
import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap


class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_ui()
        self.show()

    def config_ui(self):
        self.setWindowTitle("Des. Interfaces - Webcam PyQt6")
        self.setFixedSize(900, 650)
        self.move(100, 100)
        self.crea_widgets()

    def crea_widgets(self):
        # Label título
        lbl_titulo = QLabel("Visor de Webcam", self)
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 16px;")
        lbl_titulo.move(350, 20)

        # Label donde se mostrará el vídeo
        self.lbl_video = QLabel(self)
        self.lbl_video.move(50, 60)
        self.lbl_video.resize(800, 500)
        self.lbl_video.setStyleSheet("background-color: black;")

        # Botón Iniciar
        self.btn_iniciar = QPushButton("Iniciar", self)
        self.btn_iniciar.move(250, 580)
        self.btn_iniciar.clicked.connect(self.iniciar_camara)

        # Botón Detener
        self.btn_detener = QPushButton("Detener", self)
        self.btn_detener.move(500, 580)
        self.btn_detener.clicked.connect(self.detener_camara)

        # Timer para actualizar frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)

        self.cap = None

    def iniciar_camara(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            QMessageBox.warning(self, "Error", "No se pudo abrir la cámara")
            self.cap = None
            return

        self.timer.start(30)

    def detener_camara(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.lbl_video.clear()

    def actualizar_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w

        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # Ajustar al tamaño del QLabel
        self.lbl_video.setPixmap(pixmap.scaled(
            self.lbl_video.width(),
            self.lbl_video.height()
        ))

    def closeEvent(self, event):
        # Liberar recursos al cerrar
        self.detener_camara()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = WebcamApp()
    sys.exit(app.exec())
