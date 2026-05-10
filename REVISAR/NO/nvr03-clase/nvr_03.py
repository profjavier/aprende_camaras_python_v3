import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QLabel
)
from camara import Camara

# 🔢 CONSTANTES
ROWS = 2
COLS = 2
CELL_SPACING = 5

camaras=[
    {"mac":"", "ip":"", "id":"Portatil"},
    {"mac":"", "ip":"", "id":"Despacho"},
    {"mac":"", "ip":"", "id":"Salón"},
    {"mac":"", "ip":"", "id":"Pasillo"},
]


class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid dinámico")
        self.resize(800, 600)
        self.crear_ui()

    def crear_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        grid = QGridLayout(central)
        grid.setSpacing(CELL_SPACING)
        grid.setContentsMargins(10, 10, 10, 10)
        #grid.setContentsMargins(0, 0, 0, 0)

        for fila in range(ROWS):
            for col in range(COLS):
                cell = Camara(camaras[fila*ROWS+col].get("id"))
                grid.addWidget(cell, fila, col)

        # Que todas las filas y columnas se expandan igual
        for i in range(ROWS):
            grid.setRowStretch(i, 1)
        for j in range(COLS):
            grid.setColumnStretch(j, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GridWindow()
    win.show()
    sys.exit(app.exec())
