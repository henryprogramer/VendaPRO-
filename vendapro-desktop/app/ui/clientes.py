from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ClientesWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Gestão de Clientes"))
        self.setLayout(layout)
