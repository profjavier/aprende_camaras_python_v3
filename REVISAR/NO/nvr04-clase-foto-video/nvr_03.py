import math
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLabel
)
from camara import Camara

import util_v2

#  CONSTANTES
CELL_SPACING = 5


class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid dinámico")
        self.resize(800, 600)
        self.cargar_camaras()
        self.calcular_filas_columnas()
        self.crear_ui()

        QTimer.singleShot(500, self.activar_todas)

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
                if index < len(self.camaras):
                    cell = Camara( id = self.camaras[index].get("id"),
                               user = self.camaras[index].get("user"),
                               password = self.camaras[index].get("password"),
                               ip = self.camaras[index].get("ip"),
                               port = self.camaras[index].get("port"))
                else:
                    cell = QWidget()
                    cell.setStyleSheet("background-color: rgb(255, 255, 255);")
                grid.addWidget(cell, fila, col)

        # Que todas las filas y columnas se expandan igual
        for i in range(self.filas):
             grid.setRowStretch(i, 1)
        for j in range(self.columnas):
             grid.setColumnStretch(j, 1)

    def cargar_camaras(self):
        camaras = [
            {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.60.188", "id": "CEPY01", "user": "cepy2026", "password": "Castelar2026",
             "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.60.53", "id": "CEPY02", "user": "cepy2026", "password": "Castelar2026",
             "port": 554},
        ]
        '''self.camaras = []
        for i in range(len(camaras)):
            ip = util_v2.mac_to_ip(camaras[i]["mac"])
            if ip:
                camaras[i]["ip"] = ip
                self.camaras.append(camaras[i])'''
        self.camaras = camaras

    def calcular_filas_columnas(self):
        numero_camaras = len(self.camaras)
        self.columnas = math.ceil(math.sqrt(numero_camaras))
        self.filas = math.ceil(numero_camaras/ self.columnas)



    def activar_todas(self):
        for cam in self.findChildren(Camara):
            cam.activa_camara()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GridWindow()
    win.show()
    sys.exit(app.exec())


'''{"mac": "50-3D-D1-B8-E9-8F", "ip": "", "id": "CEPY03", "user": "cepy2026", "password": "Castelar2026",
             "port": 554},
             {"mac": "50-3D-D1-B8-F6-ED", "ip": "", "id": "CEPY04", "user": "cepy2026", "password": "Castelar2026",
              "port": 554},
             {"mac": "E0-D3-62-28-80-06", "ip": "", "id": "CEPY05", "user": "cepy2026","password": "Castelar2026",
              "port": 554},
            {"mac": "E0-D3-62-28-71-EE", "ip": "", "id": "CEPY06", "user": "cepy2026","password": "Castelar2026",
             "port": 554},
            {"mac": "CC-BA-BD-22-C0-4D", "ip": "", "id": "CEPY07", "user": "cepy2026","password": "Castelar2026",
             "port": 554},
            {"mac": "CC-BA-BD-22-BA-65", "ip": "9", "id": "CEPY09", "user": "cepy2026","password": "Castelar2026",
             "port": 554},'''