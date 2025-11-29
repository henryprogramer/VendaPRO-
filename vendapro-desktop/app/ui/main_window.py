from PyQt5.QtWidgets import QMainWindow
from .painel import PainelWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VendaPRO - Desktop")
        self.resize(1200, 700)

        self.painel = PainelWindow()
        self.setCentralWidget(self.painel)
