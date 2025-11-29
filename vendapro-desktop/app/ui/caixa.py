from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class CaixaWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Caixa"))
        self.setLayout(layout)
