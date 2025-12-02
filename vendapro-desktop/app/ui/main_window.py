import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation

# imports das páginas
from app.ui.painel import PainelWindow
from app.ui.biblioteca import BibliotecaWindow
from app.ui.caixa import CaixaWindow
from app.ui.clientes import ClientesWindow
from app.ui.delivery import DeliveryWindow
from app.ui.estoque import EstoqueWindow
from app.ui.fornecedores import FornecedoresWindow
from app.ui.funcionarios import FuncionariosWindow
from app.ui.produtos import ProdutosWindow
from app.ui.vendas import VendasWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VendaPRO - Desktop")
        self.resize(800, 400)

        # Caminho da logo
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "images", "logo.png")
        print("ICON PATH:", icon_path)
        print("EXISTS:", os.path.exists(icon_path))

        self.setWindowIcon(QIcon(icon_path))

        # ======================================================
        #  CONTAINER PRINCIPAL
        # ======================================================
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =============================
        #        HEADER SUPERIOR
        # =============================
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(0)

        # Botão menu (toggle sidebar)
        self.btn_toggle_menu = QPushButton("☰")
        self.btn_toggle_menu.setFixedSize(40, 40)
        self.btn_toggle_menu.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                background-color: #1f2937;
                border-radius: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        self.btn_toggle_menu.clicked.connect(self.toggle_sidebar)

        # LOGO CENTRALIZADA
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(icon_path)

        if pixmap.isNull():
            print("ERRO: imagem não carregou")
        else:
            pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)


        # "Spacer" invisível para forçar centralização real
        left_spacer = QWidget()
        right_spacer = QWidget()
        left_spacer.setSizePolicy(self.btn_toggle_menu.sizePolicy())
        right_spacer.setSizePolicy(self.btn_profile.sizePolicy() if hasattr(self, "btn_profile") else self.btn_toggle_menu.sizePolicy())

        # Botão perfil (direita)
        self.btn_profile = QPushButton("•")
        self.btn_profile.setFixedSize(45, 45)
        self.btn_profile.setStyleSheet("""
            QPushButton {
                font-size: 26px;
                color: white;
                background-color: #2563eb;
                border-radius: 22px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        #
        # ORDEM: [menu] [left spacer] [logo] [right spacer] [btn perfil]
        #
        header_layout.addWidget(self.btn_toggle_menu)
        header_layout.addWidget(left_spacer)
        header_layout.addWidget(logo_label, stretch=1)
        header_layout.addWidget(right_spacer)
        header_layout.addWidget(self.btn_profile)

        # ======================================================
        #  ÁREA CENTRAL
        # ======================================================
        center_frame = QFrame()
        center_frame.setStyleSheet("background-color: #111827;")  # COR ESCURA RESTAURADA

        center_layout = QHBoxLayout(center_frame)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # ======================================================
        #  SIDEBAR
        # ======================================================
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)

        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #0f172a;
                color: #cbd5e1;
                font-size: 15px;
                padding-top: 12px;
                border-right: 1px solid rgba(255,255,255,0.08);
            }

            QListWidget::item {
                padding: 14px;
                margin: 6px 10px;
                border-radius: 10px;
            }

            QListWidget::item:selected {
                background-color: rgba(45,125,255,0.22);
                border-left: 3px solid #2d7dff;
                color: white;
            }

            QListWidget::item:hover {
                background-color: rgba(255,255,255,0.04);
            }
        """)

        # Mapeamento das páginas
        self.pages_map = {
            "Painel": PainelWindow,
            "Caixa": CaixaWindow,
            "Clientes": ClientesWindow,
            "Produtos": ProdutosWindow,
            "Estoque": EstoqueWindow,
            "Fornecedores": FornecedoresWindow,
            "Funcionários": FuncionariosWindow,
            "Vendas": VendasWindow,
            "Delivery": DeliveryWindow,
            "Biblioteca": BibliotecaWindow
        }

        # Adicionar itens
        for name in self.pages_map:
            self.sidebar.addItem(QListWidgetItem(name))

        self.sidebar.currentItemChanged.connect(self.load_page)

        # Página inicial
        self.current_page = PainelWindow()

        # Montagem
        center_layout.addWidget(self.sidebar)
        center_layout.addWidget(self.current_page)

        main_layout.addWidget(header)
        main_layout.addWidget(center_frame)

        self.setCentralWidget(main_container)

        # Estado e animação da sidebar
        self.sidebar_expanded = True
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(200)

        # Seleção inicial
        self.sidebar.setCurrentRow(0)

    # ======================================================
    #  TROCA DE PÁGINAS
    # ======================================================
    def load_page(self, current, previous):
        if not current:
            return

        page_name = current.text()
        PageClass = self.pages_map[page_name]

        # Capturar o layout do center_frame
        center_frame = self.centralWidget().layout().itemAt(1).widget()
        center_layout = center_frame.layout()

        center_layout.removeWidget(self.current_page)
        self.current_page.deleteLater()

        self.current_page = PageClass()
        center_layout.addWidget(self.current_page)

    # ======================================================
    #  TOGGLE MENU COM ANIMAÇÃO
    # ======================================================
    def toggle_sidebar(self):
        expanded = 240
        collapsed = 0

        start = expanded if self.sidebar_expanded else collapsed
        end = collapsed if self.sidebar_expanded else expanded

        # Remove qualquer trava de width
        self.sidebar.setMinimumWidth(start)
        self.sidebar.setMaximumWidth(start)

        self.sidebar_animation.stop()
        self.sidebar_animation.setStartValue(start)
        self.sidebar_animation.setEndValue(end)
        self.sidebar_animation.start()

        # A cada frame, sincroniza min/max
        self.sidebar_animation.valueChanged.connect(
            lambda value: (
                self.sidebar.setMinimumWidth(value),
                self.sidebar.setMaximumWidth(value)
            )
        )

        self.sidebar_expanded = not self.sidebar_expanded
