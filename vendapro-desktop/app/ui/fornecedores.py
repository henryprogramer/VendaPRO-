from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class FornecedoresWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Fornecedores"))
        self.setLayout(layout)
