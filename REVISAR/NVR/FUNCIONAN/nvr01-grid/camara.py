import random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class Camara(QWidget):
    def __init__(self, id=""):
        super(Camara, self).__init__()
        self.id = id
        self.crear_celda()

    def crear_celda(self):

        # Color aleatorio
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: rgb({r},{g},{b});
                border-radius: 8px;
            }}
            """
        )

        label = QLabel(f"Camara {self.id}", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold;"
        )

        # Layout interno de la celda

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)

