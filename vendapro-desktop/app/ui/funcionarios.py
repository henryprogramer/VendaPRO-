from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class FuncionariosWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Funcionários"))
        self.setLayout(layout)
