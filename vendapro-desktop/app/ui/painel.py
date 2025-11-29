from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class PainelWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Painel Principal"))
        self.setLayout(layout)
