from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class BibliotecaWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Biblioteca"))
        self.setLayout(layout)
