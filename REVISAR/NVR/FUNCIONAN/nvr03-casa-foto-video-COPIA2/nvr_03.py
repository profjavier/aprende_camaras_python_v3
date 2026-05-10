import math
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout
)
from camara import Camara
import util

#  CONSTANTES
CELL_SPACING = 5


class GridWindow(QMainWindow):
    SUBRED = "192.168.6.0/24"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid dinámico")
        self.resize(800, 600)
        self.cargar_camaras()
        self.calcular_filas_columnas()
        self.crear_ui()

    def crear_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setSpacing(CELL_SPACING)
        grid.setContentsMargins(10, 10, 10, 10)

        self.visor_camaras = []
        for fila in range(self.filas):
            for col in range(self.columnas):
                index = fila * self.columnas + col
                if index < len(self.camaras_config):
                    cell = Camara( id = self.camaras_config[index].get("id"),
                               user = self.camaras_config[index].get("user"),
                               password = self.camaras_config[index].get("password"),
                               ip = self.camaras_config[index].get("ip"),
                               port = self.camaras_config[index].get("port"))
                    self.visor_camaras.append(cell)
                else:
                    cell = QWidget()
                    cell.setStyleSheet("background-color: rgb(255, 255, 255);")
                grid.addWidget(cell, fila, col)

        for cell in self.visor_camaras:
            cell.activa_camara()

    def cargar_camaras(self):
        '''self.camaras_config =  [
            # Casa
            {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.60.188", "id": "CEPY01", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.60.53", "id": "CEPY02", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
        ]'''
        self.camaras_config = [
            # Casa
            {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier",
             "password": "Castelar2026", "port": 554},
            #
            {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.60.188", "id": "CEPY01", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.60.53", "id": "CEPY02", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50-3D-D1-B8-E9-8F", "ip": "", "id": "CEPY03", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50-3D-D1-B8-F6-ED", "ip": "", "id": "CEPY04", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "E0-D3-62-28-80-06", "ip": "", "id": "CEPY05", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "E0-D3-62-28-71-EE", "ip": "", "id": "CEPY06", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "CC-BA-BD-22-C0-4D", "ip": "", "id": "CEPY07", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "CC-BA-BD-22-BA-65", "ip": "9", "id": "CEPY09", "user": "cepy2026",
             "password": "Castelar2026", "port": 554}
        ]

        # Obtener todas las MACs
        macs = [camara["mac"] for camara in self.camaras_config]
        macs_to_ip = util.mac_to_ip(self.SUBRED,macs)

        self.camaras_activas_config = []
        for camara_cfg in self.camaras_config:
            if macs_to_ip.get( camara_cfg['mac'].lower().replace("-", ":"), None):
                self.camaras_activas_config.append(camara_cfg)

    def calcular_filas_columnas(self):
        numero_camaras = len(self.camaras_config)
        self.columnas = math.ceil(math.sqrt(numero_camaras))
        self.filas = math.ceil(numero_camaras/ self.columnas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GridWindow()
    win.show()
    sys.exit(app.exec())


'''
self.camaras_config =  [
            # Casa
            {"mac": "EC:75:0C:12:2F:83", "ip": "192.168.1.200", "id": "Casa", "user": "javier",
             "password": "Castelar2026", "port": 554},
            #
            {"mac": "50:3D:D1:B8:DB:CF", "ip": "192.168.60.188", "id": "CEPY01", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50:3D:D1:B8:E9:F4", "ip": "192.168.60.53", "id": "CEPY02", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50-3D-D1-B8-E9-8F", "ip": "", "id": "CEPY03", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "50-3D-D1-B8-F6-ED", "ip": "", "id": "CEPY04", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "E0-D3-62-28-80-06", "ip": "", "id": "CEPY05", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "E0-D3-62-28-71-EE", "ip": "", "id": "CEPY06", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "CC-BA-BD-22-C0-4D", "ip": "", "id": "CEPY07", "user": "cepy2026",
             "password": "Castelar2026", "port": 554},
            {"mac": "CC-BA-BD-22-BA-65", "ip": "9", "id": "CEPY09", "user": "cepy2026",
             "password": "Castelar2026", "port": 554}
        ]
'''