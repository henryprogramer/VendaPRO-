from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class ProdutosWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Gestão de Produtos"))
        self.setLayout(layout)
