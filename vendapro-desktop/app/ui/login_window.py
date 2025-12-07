# app/ui/login_window.py
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# IMPORTS PÓS-FUNÇÃO PARA EVITAR CICLO
from app.database.user_repository import validate_login_for_company, get_all_companies

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VendaPRO - Login")
        self.setFixedSize(420, 520)

        self.setStyleSheet("""
            QWidget { background-color: #0f172a; color: #e2e8f0; font-size: 15px; }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QLineEdit:focus { border: 1px solid #2563eb; }
            QPushButton {
                background-color: #2563eb;
                padding: 12px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # LOGO
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_path, "assets", "images", "logo.png")

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        layout.addWidget(logo)

        # COMBO BOX EMPRESAS
        self.company_select = QComboBox()
        self.refresh_companies()
        layout.addWidget(self.company_select)

        # CAMPOS DE LOGIN
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuário")

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Senha")
        self.input_pass.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.input_user)
        layout.addWidget(self.input_pass)

        # BOTÃO LOGIN
        self.btn_login = QPushButton("Entrar")
        self.btn_login.clicked.connect(self.try_login)
        layout.addWidget(self.btn_login)

        # LINK REGISTRO
        self.btn_register = QPushButton("Criar nova empresa / usuário")
        self.btn_register.setStyleSheet("""
            QPushButton {
                border: none;
                color: #60a5fa;
                background: transparent;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #93c5fd;
                text-decoration: underline;
            }
        """)
        self.btn_register.clicked.connect(self.open_register)
        layout.addWidget(self.btn_register, alignment=Qt.AlignCenter)

        layout.addStretch()

    # REFRESH EMPRESAS
    def refresh_companies(self):
        companies = get_all_companies()
        self.company_map = {name: cid for cid, name in companies}
        self.company_select.clear()
        self.company_select.addItems([name for cid, name in companies])

    # LÓGICA DE LOGIN
    def try_login(self):
        user = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        company_name = self.company_select.currentText()  # <--- usa nome, não ID

        if not user or not password or not company_name:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        user_data = validate_login_for_company(company_name, user, password)

        if user_data:
            self.open_main(user_data)
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
 
    # ABRIR REGISTRO
    def open_register(self):
        from app.ui.register_window import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

    # ABRIR JANELA PRINCIPAL
    def open_main(self, user_data):
        from app.ui.main_window import MainWindow
        self.main = MainWindow(user_data)
        self.main.show()
        self.close()
