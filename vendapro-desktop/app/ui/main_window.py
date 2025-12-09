# app/ui/main_window.py
import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QFrame, QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve

# imports das páginas
from app.ui.login_window import LoginWindow
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
    def __init__(self, user_data):
        super().__init__()

        self.user = user_data
        self.company_name = user_data.get("company_name")

        self.setWindowTitle("VendaPRO - Desktop")
        self.resize(1100, 650)

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_path, "assets", "images", "logo.png")
        avatar_path = os.path.join(base_path, "assets", "images", "user_default.png")
        logo_path = os.path.join(base_path, "assets", "images", "logo_default.png")

        self.setWindowIcon(QIcon(icon_path))

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # HEADER
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("QFrame { background-color: #111827; border-bottom: 1px solid rgba(255,255,255,0.08); }")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.btn_toggle_menu = QPushButton("☰")
        self.btn_toggle_menu.setFixedSize(42, 42)
        self.btn_toggle_menu.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                background-color: #1f2937;
                border-radius: 8px;
                color: white;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        self.btn_toggle_menu.clicked.connect(self.toggle_sidebar)

        # LOGO CENTRO
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # ----------------------- FOTOS USUÁRIO + EMPRESA -----------------------
        def pixmap_from_bytes(bytes_data, fallback_path):
            pixmap = QPixmap()
            if bytes_data:
                if isinstance(bytes_data, memoryview):
                    bytes_data = bytes_data.tobytes()
                pixmap.loadFromData(bytes_data)
            else:
                pixmap.load(fallback_path)
            return pixmap

        def circular_pixmap(pixmap, size=50):
            pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            rounded = QPixmap(size, size)
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            return rounded

        from app.database.user_repository import get_user_by_id, get_company_logo

        # Pega usuário pelo ID
        user_id = self.user.get("id")
        user_data = get_user_by_id(self.company_name, user_id)

        user_bytes = user_data.get("photo") if user_data else None
        company_bytes = get_company_logo(self.company_name)

        pixmap_user = pixmap_from_bytes(user_bytes, avatar_path)
        pixmap_company = pixmap_from_bytes(company_bytes, logo_path)

        # ----------------------- BOTÕES USUÁRIO + EMPRESA -----------------------
        self.btn_user = QPushButton()
        self.btn_user.setFixedSize(50, 50)
        self.btn_user.setStyleSheet("border:none; border-radius:25px;")
        self.btn_user.clicked.connect(self.toggle_profile_card)

        self.btn_company = QPushButton()
        self.btn_company.setFixedSize(50, 50)
        self.btn_company.setStyleSheet("border:none; border-radius:25px;")
        self.btn_company.clicked.connect(self.toggle_profile_card)

        # Container horizontal para os botões
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(4)
        btn_layout.addWidget(self.btn_user)
        btn_layout.addWidget(self.btn_company)

        # ----------------------- DEFININDO ÍCONES -----------------------
        pixmap_user = pixmap_from_bytes(user_bytes, avatar_path)
        pixmap_company = pixmap_from_bytes(company_bytes, logo_path)

        self.btn_user.setIcon(QIcon(circular_pixmap(pixmap_user)))
        self.btn_user.setIconSize(pixmap_user.size())

        self.btn_company.setIcon(QIcon(circular_pixmap(pixmap_company)))
        self.btn_company.setIconSize(pixmap_company.size())


        # ----------------- ADICIONA AO HEADER -----------------
        left_spacer = QWidget()
        right_spacer = QWidget()
        header_layout.addWidget(self.btn_toggle_menu)
        header_layout.addWidget(left_spacer)
        header_layout.addWidget(logo_label, stretch=1)
        header_layout.addWidget(right_spacer)
        header_layout.addWidget(btn_container)

        # CENTER
        center_frame = QFrame()
        center_frame.setStyleSheet("background-color: #111827;")
        center_layout = QHBoxLayout(center_frame)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # SIDEBAR
        self.sidebar = QListWidget()
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(240)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #0f172a;
                color: #cbd5e1;
                font-size: 15px;
                padding-top: 12px;
                border-right: 1px solid rgba(255,255,255,0.08);
            }
            QListWidget::item { padding: 14px; margin: 6px 10px; border-radius: 10px; }
            QListWidget::item:selected {
                background-color: rgba(45,125,255,0.22);
                border-left: 3px solid #2d7dff;
                color: white;
            }
            QListWidget::item:hover { background-color: rgba(255,255,255,0.04); }
        """)

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

        for name in self.pages_map:
            self.sidebar.addItem(QListWidgetItem(name))

        self.sidebar.currentItemChanged.connect(self.load_page)
        self.current_page = PainelWindow()
        center_layout.addWidget(self.sidebar)
        center_layout.addWidget(self.current_page)

        main_layout.addWidget(header)
        main_layout.addWidget(center_frame)
        self.setCentralWidget(main_container)

        self.sidebar_expanded = True
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.sidebar_animation.setDuration(200)
        self.sidebar.setCurrentRow(0)

        self.profile_card = None
        self.profile_card_visible = False

    # ----------------- PROFILE CARD FLUTUANTE -------------------
    def create_profile_card(self):
        import os
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
        from PyQt5.QtCore import Qt

        card = QFrame(self)
        card.setFixedSize(220, 300)
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                color: #fff;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        photos_layout = QHBoxLayout()
        photos_layout.setSpacing(12)

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        default_user_path = os.path.join(base_path, "assets", "images", "user_default.png")
        default_logo_path = os.path.join(base_path, "assets", "images", "logo_default.png")

        def pixmap_from_bytes(bytes_data, fallback_path):
            pixmap = QPixmap()
            if bytes_data:
                if isinstance(bytes_data, memoryview):
                    bytes_data = bytes_data.tobytes()
                pixmap.loadFromData(bytes_data)
            else:
                pixmap.load(fallback_path)
            return pixmap

        def circular_pixmap(pixmap, size=60):
            pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            rounded = QPixmap(size, size)
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            return rounded

        # Pega fotos reais do banco
        from app.database.user_repository import get_user_by_id, get_company_logo
        user_id = self.user.get("id")
        user_data = get_user_by_id(self.company_name, user_id)
        user_bytes = user_data.get("photo") if user_data else None
        company_bytes = get_company_logo(self.company_name)

        user_pixmap = circular_pixmap(pixmap_from_bytes(user_bytes, default_user_path))
        company_pixmap = circular_pixmap(pixmap_from_bytes(company_bytes, default_logo_path))

        # Labels de fotos
        user_label = QLabel()
        user_label.setPixmap(user_pixmap)
        user_label.setAlignment(Qt.AlignCenter)
        photos_layout.addWidget(user_label)

        company_label = QLabel()
        company_label.setPixmap(company_pixmap)
        company_label.setAlignment(Qt.AlignCenter)
        photos_layout.addWidget(company_label)

        layout.addLayout(photos_layout)

        # Informações da empresa e usuário
        lbl_empresa = QLabel(self.user.get("company_name", "Empresa"))
        lbl_empresa.setAlignment(Qt.AlignCenter)
        lbl_empresa.setStyleSheet("font-weight:bold; font-size:14px; margin-top:4px;")
        layout.addWidget(lbl_empresa)

        layout.addWidget(QLabel(f"Usuário: {self.user.get('username', 'desconhecido')}"))
        layout.addWidget(QLabel(f"ID: {self.user.get('id', 'N/A')}"))

        # Botões Fechar e Sair
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(lambda: self.toggle_profile_card())
        layout.addWidget(btn_close)

        btn_logout = QPushButton("Sair")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        card.hide()
        return card

    # ----------------- TOGGLE PROFILE CARD -------------------
    def toggle_profile_card(self, use_company=False, offset_x=0):
        if not hasattr(self, "profile_card") or self.profile_card is None:
            self.profile_card = self.create_profile_card()
            self.profile_card.setParent(self)
            self.profile_card.raise_()

        if self.profile_card.isVisible():
            self.profile_card.hide()
        else:
            # Pega botão referência
            btn_ref = self.btn_company if use_company else self.btn_user
            btn_pos = btn_ref.mapTo(self, QPoint(0, 0))  # posição relativa à janela
            x = btn_pos.x() + offset_x
            y = btn_pos.y() + btn_ref.height() + 2

            # Mantém o card dentro da janela
            x = max(0, min(x, self.width() - self.profile_card.width()))
            y = max(0, min(y, self.height() - self.profile_card.height()))

            self.profile_card.move(x, y)
            self.profile_card.show()
            self.profile_card.raise_()

        self.profile_card_visible = not self.profile_card_visible

    def logout(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    # ---------------- PAGES ------------------
    def load_page(self, current, previous):
        if not current:
            return 
        page_name = current.text()
        PageClass = self.pages_map[page_name]

        center_frame = self.centralWidget().layout().itemAt(1).widget()
        center_layout = center_frame.layout()

        center_layout.removeWidget(self.current_page)
        self.current_page.deleteLater()

        try:
            self.current_page = PageClass(self.company_name)
        except TypeError:
            self.current_page = PageClass()

        center_layout.addWidget(self.current_page)

    # ---------------- SIDEBAR ------------------
    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
