from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class EstoqueWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Controle de Estoque"))
        self.setLayout(layout)
