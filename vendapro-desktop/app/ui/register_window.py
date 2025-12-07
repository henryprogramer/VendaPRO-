import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QMessageBox, QComboBox, QHBoxLayout, QInputDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from app.database.user_repository import create_company, create_user, get_all_companies

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.company_logo_bytes = None
        self.user_photo_bytes = None

        self.setWindowTitle("VendaPRO - Cadastro")
        self.setFixedSize(420, 700)

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
            QComboBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
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

        # TÍTULO
        title = QLabel("Cadastrar Usuário / Empresa")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # COMBOBOX PARA EMPRESAS + BOTÃO NOVA EMPRESA
        hbox_company = QHBoxLayout()
        self.combo_company = QComboBox()
        self.load_companies()
        hbox_company.addWidget(self.combo_company)

        self.btn_new_company = QPushButton("Nova Empresa")
        self.btn_new_company.clicked.connect(self.create_new_company_dialog)
        hbox_company.addWidget(self.btn_new_company)

        layout.addLayout(hbox_company)

        # BOTÃO PARA UPLOAD FOTO DO USUÁRIO
        self.btn_user_photo = QPushButton("Enviar foto do usuário")
        self.btn_user_photo.clicked.connect(self.upload_user_photo)
        layout.addWidget(self.btn_user_photo)

        # CAMPOS DE USUÁRIO
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
    # CARREGA EMPRESAS EXISTENTES
    # ========================
    def load_companies(self):
        companies = get_all_companies()
        self.combo_company.clear()
        for c in companies:
            if isinstance(c, tuple):
                self.combo_company.addItem(c[1])
            else:
                self.combo_company.addItem(str(c))

    # ========================
    # CADASTRO DE NOVA EMPRESA
    # ========================
    def create_new_company_dialog(self):
        name, ok = QInputDialog.getText(self, "Nova Empresa", "Nome da empresa:")
        if not ok or not name.strip():
            return

        # Upload de logo opcional
        file_path, _ = QFileDialog.getOpenFileName(self, "Escolher Logo da Empresa", "", "Imagens (*.png *.jpg *.jpeg)")
        logo_bytes = None
        if file_path:
            with open(file_path, "rb") as f:
                logo_bytes = f.read()

        company_id = create_company(name.strip(), logo_bytes)
        if company_id is None:
            self.show_error("Essa empresa já existe.")
            return

        QMessageBox.information(self, "Sucesso", f"Empresa '{name.strip()}' criada!")
        self.load_companies()
        self.combo_company.setCurrentText(name.strip())

    # ========================
    # UPLOAD FOTO USUÁRIO
    # ========================
    def upload_user_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto do Usuário", "", "Imagens (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        with open(file_path, "rb") as img:
            self.user_photo_bytes = img.read()
        QMessageBox.information(self, "OK", "Foto adicionada com sucesso!")

    # ========================
    # CADASTRO DE NOVO USUÁRIO
    # ========================
    def do_register(self):
        company = self.combo_company.currentText()
        user = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        confirm = self.input_pass_confirm.text().strip()

        if not company or not user or not password or not confirm:
            self.show_error("Preencha todos os campos.")
            return

        if password != confirm:
            self.show_error("As senhas não coincidem.")
            return

        ok = create_user(company, user, password, self.user_photo_bytes)
        if not ok:
            self.show_error("Usuário já existe para esta empresa.")
            return

        self.show_msg(f"Usuário criado com sucesso para a empresa '{company}'!")
        self.voltar_login()
 
    # ========================
    # MÉTODOS DE AJUDA
    # ========================
    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)

    def show_msg(self, msg):
        QMessageBox.information(self, "Sucesso", msg)

    def voltar_login(self):
        from app.ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
