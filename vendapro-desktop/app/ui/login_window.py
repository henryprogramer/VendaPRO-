# app/ui/login_window.py
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from app.ui.main_window import MainWindow
from app.ui.register_window import RegisterWindow
from app.database.user_repository import validate_login


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VendaPRO - Login")
        self.setFixedSize(420, 520)

        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-size: 15px;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2563eb;
            }
            QPushButton {
                background-color: #2563eb;
                padding: 12px;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # LOGO
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_path, "assets", "images", "logo.png")

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        layout.addWidget(logo)

        # CAMPOS
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

        # LINK CADASTRO
        self.btn_register = QPushButton("Não tem uma conta? Crie uma aqui")
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

    # ==============================
    #        LÓGICA LOGIN
    # ==============================
    def try_login(self):
        user = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if user == "" or password == "":
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        if validate_login(user, password):
            self.open_main()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")

    # ==============================
    #      ABERTURA DE JANELAS
    # ==============================
    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

    def open_main(self):
        self.main = MainWindow()
        self.main.show()
        self.close()
