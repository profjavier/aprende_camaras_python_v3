import random
import cv2
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QStackedLayout
from ventana_camara import VentanaCamara


class VideoThread(QThread):
    frame_ready = pyqtSignal(object)  # señal que envía el frame a la GUI

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = True
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            print("No se pudo abrir la cámara:", self.rtsp_url)
            return

        while self.running:
            self.cap.grab()  # tomar el último frame disponible
            ret, frame = self.cap.retrieve()
            if ret:
                self.frame_ready.emit(frame)

    def stop(self):
        self.running = False
        self.wait()
        if self.cap:
            self.cap.release()
