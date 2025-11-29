from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class VendasWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Vendas"))
        self.setLayout(layout)
