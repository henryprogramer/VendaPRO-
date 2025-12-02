from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CardInfo(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setFixedHeight(90)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; color: #cccccc;")

        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addStretch()


class PainelWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #0d1b2a;
                color: white;
                font-family: 'Segoe UI';
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ============================
        #  HEADER COM GRADIENTE
        # ============================
        header = QFrame()
        header.setFixedHeight(150)
        header.setStyleSheet("""
            QFrame {
                border-radius: 16px;
                background: aqua;
            }
        """)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(25, 20, 25, 20)

        welcome = QLabel("Bem-vindo, Chefe!😄")
        welcome.setStyleSheet("font-size: 26px; font-weight: 500; color: #002c5c;")

        header_layout.addWidget(welcome)
        header_layout.addStretch()

        # ============================
        #  CARDS + BOTÃO NOVA VENDA
        # ============================
        cards_row = QHBoxLayout()
        cards_row.setSpacing(15)

        vendas_card = CardInfo("VENDAS HOJE", 150)
        clientes_card = CardInfo("CLIENTES", 36)

        nova_venda_btn = QPushButton("NOVA VENDA")
        nova_venda_btn.setFixedSize(160, 50)
        nova_venda_btn.setCursor(Qt.PointingHandCursor)
        nova_venda_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d7dff;
                color: white;
                font-size: 16px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1b63d1;
            }
        """)

        cards_row.addWidget(vendas_card)
        cards_row.addWidget(clientes_card)
        cards_row.addWidget(nova_venda_btn)

        # ============================
        #  CARD CENTRAL — MENSAGEM
        # ============================
        msg_card = QFrame()
        msg_card.setFixedHeight(150)
        msg_card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.07);
                border-radius: 16px;
            }
            QLabel {
                color: white;
            }
        """)

        msg_layout = QVBoxLayout(msg_card)
        msg_layout.setContentsMargins(20, 20, 20, 20)

        title_msg = QLabel("O sistema que vai aumentar suas vendas")
        title_msg.setStyleSheet("font-size: 22px; font-weight: bold;")

        desc_msg = QLabel("Venda com mais velocidade através do VendaPRO")
        desc_msg.setStyleSheet("font-size: 14px; color: #cccccc;")

        msg_layout.addWidget(title_msg)
        msg_layout.addWidget(desc_msg)
        msg_layout.addStretch()

        # ============================
        #  ORGANIZAÇÃO NA TELA
        # ============================
        main_layout.addWidget(header)
        main_layout.addLayout(cards_row)
        main_layout.addWidget(msg_card)
        main_layout.addStretch()
