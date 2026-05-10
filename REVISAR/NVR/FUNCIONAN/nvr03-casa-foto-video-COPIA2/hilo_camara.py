from PyQt6.QtCore import QObject, QThread, pyqtSignal

class HiloCamara(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, camara):
        super().__init__()
        self.camara = camara

    def run(self):
        self.camara.iniciar_conexion()
        self.finished.emit(True)
