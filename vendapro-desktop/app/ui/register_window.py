# app/ui/register_window.py
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from app.database.user_repository import create_user


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VendaPRO - Cadastro")
        self.setFixedSize(420, 560)

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
        layout.setSpacing(25)

        # LOGO
        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_path, "assets", "images", "logo.png")

        pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        layout.addWidget(logo)

        # CAMPOS
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuário")

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Senha")
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.input_pass_confirm = QLineEdit()
        self.input_pass_confirm.setPlaceholderText("Confirmar Senha")
        self.input_pass_confirm.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.input_user)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.input_pass_confirm)

        # BOTÃO CADASTRAR
        self.btn_register = QPushButton("Cadastrar")
        self.btn_register.clicked.connect(self.do_register)
        layout.addWidget(self.btn_register)

        # BOTÃO VOLTAR
        self.btn_back = QPushButton("Voltar ao login")
        self.btn_back.setStyleSheet("""
            QPushButton {
                border: none;
                color: #60a5fa;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #93c5fd;
                text-decoration: underline;
            }
        """)
        self.btn_back.clicked.connect(self.voltar_login)
        layout.addWidget(self.btn_back)

        layout.addStretch()

    # ========================
    #      LÓGICA CADASTRO
    # ========================
    def do_register(self):
        user = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        confirm = self.input_pass_confirm.text().strip()

        if user == "" or password == "" or confirm == "":
            self.show_error("Preencha todos os campos.")
            return

        if password != confirm:
            self.show_error("As senhas não coincidem.")
            return

        ok = create_user(user, password)

        if not ok:
            self.show_error("Usuário já existe.")
            return

        self.show_msg("Usuário criado com sucesso!")
        self.voltar_login()

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)

    def show_msg(self, msg):
        QMessageBox.information(self, "Sucesso", msg)

    def voltar_login(self):
        from app.ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
