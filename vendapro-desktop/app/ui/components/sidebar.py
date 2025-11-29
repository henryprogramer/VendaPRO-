from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .nav_button import NavButton

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(NavButton("Painel"))
        layout.addWidget(NavButton("Caixa"))
        layout.addWidget(NavButton("Clientes"))
        layout.addWidget(NavButton("Produtos"))
        layout.addWidget(NavButton("Estoque"))
        layout.addWidget(NavButton("Fornecedores"))
        layout.addWidget(NavButton("Vendas"))
        layout.addWidget(NavButton("Delivery"))
        layout.addWidget(NavButton("Biblioteca"))

        self.setLayout(layout)
