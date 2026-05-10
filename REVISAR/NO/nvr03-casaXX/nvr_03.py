import math
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLabel
)
from camara import Camara

#  CONSTANTES
CELL_SPACING = 5


class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid dinámico")
        self.resize(800, 600)
        self.visores_camaras = []
        self.cargar_configuraciones_camaras()
        self.calcular_filas_columnas()
        self.crear_ui()

        # Ejecutar post_init justo después de que Qt esté listo
        QTimer.singleShot(0, self.post_init)

    def post_init(self):
        print("Método después del constructor")
        for visor in self.visores_camaras:
            visor.activa_camara()

    def crear_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setSpacing(CELL_SPACING)
        grid.setContentsMargins(10, 10, 10, 10)
        #grid.setContentsMargins(0, 0, 0, 0)

        for fila in range(self.filas):
            for col in range(self.columnas):
                # index = fila*self.filas+col
                index = fila * self.columnas + col
                if index < len(self.config_camaras):
                    cell = Camara( id = self.config_camaras[index].get("id"),
                               user = self.config_camaras[index].get("user"),
                               password = self.config_camaras[index].get("password"),
                               ip = self.config_camaras[index].get("ip"),
                               port = self.config_camaras[index].get("port"))
                    self.visores_camaras.append(cell)
                else:
                    cell = QWidget()
                    cell.setStyleSheet("background-color: rgb(255, 255, 255);")
                grid.addWidget(cell, fila, col)

        # Que todas las filas y columnas se expandan igual
        # for i in range(ROWS):
        #     grid.setRowStretch(i, 1)
        # for j in range(COLS):
        #     grid.setColumnStretch(j, 1)

        # for visor in self.visores_camaras:
        #     visor.activa_camara()

    def cargar_configuraciones_camaras(self):
        self.config_camaras = [
            {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier", "password": "Castelar2026",
             "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02", "user": "CEPY2026", "password": "Castelar2026",
             "port": 554},
            # {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.1.39", "id": "Jardin", "user": "CEPY2026", "password": "Castelar2026",
            #  "port": 554},
            # {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier", "password": "Castelar2026",
            #  "port": 554},
            # {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.1.129", "id": "CEPY02", "user": "CEPY2026","password": "Castelar2026",
            #  "port": 554},
        ]

    def calcular_filas_columnas(self):
        numero_camaras = len(self.config_camaras)
        self.columnas = math.ceil(math.sqrt(numero_camaras))
        self.filas = math.ceil(numero_camaras/ self.columnas)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GridWindow()
    win.show()
    sys.exit(app.exec())
