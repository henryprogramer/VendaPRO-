from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor

from app.database.user_repository import (
    get_all_funcionarios,
    create_funcionario,
    update_funcionario,
    delete_funcionario
)

# ========== ICONES VETORIAIS ======================================

def make_icon(paint_fn, size=16, color=QColor("white")):
    pix = QPixmap(size, size)
    pix.fill(QColor(0,0,0,0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(color)
    p.setBrush(color)
    path = QPainterPath()
    paint_fn(path, size)
    p.drawPath(path)
    p.end()
    return QIcon(pix)

def icon_eye():
    def paint(path, s):
        path.addEllipse(s*0.1, s*0.3, s*0.8, s*0.4)
        path.addEllipse(s*0.4, s*0.4, s*0.2, s*0.2)
    return make_icon(paint)

def icon_pencil():
    def paint(path, s):
        path.moveTo(s*0.2, s*0.8)
        path.lineTo(s*0.8, s*0.2)
        path.lineTo(s*0.9, s*0.3)
        path.lineTo(s*0.3, s*0.9)
        path.closeSubpath()
    return make_icon(paint)

def icon_trash():
    def paint(path, s):
        path.addRect(s*0.2, s*0.3, s*0.6, s*0.5)
        path.addRect(s*0.15, s*0.2, s*0.7, s*0.1)
    return make_icon(paint)


# ========== UTIL BOTÕES ======================================

def make_action_btn(text, bg):
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg};
            padding: 4px 10px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {bg}CC;
        }}
    """)
    
    return btn
# ========== DIALOG ADD FUNCIONÁRIO ====================================

class AddFuncionarioDialog(QDialog):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.photo_bytes = None  # inicializa foto
        self.setWindowTitle("Novo Funcionário")
        self.setStyleSheet(CRUD_STYLE)

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.cargo_input = QLineEdit()
        self.address_input = QLineEdit()

        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Cargo:", self.cargo_input)
        form.addRow("Endereço:", self.address_input)

        # Foto
        self.photo_label = QLabel()
        pixmap = QPixmap("assets/images/user_default.png").scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo_label.setPixmap(pixmap)
        btn_photo = QPushButton("Selecionar Foto")
        btn_photo.clicked.connect(self.select_photo)
        form.addRow(btn_photo, self.photo_label)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)
        self.setLayout(form)

    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
            with open(file_path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
            return

        create_funcionario(
            self.company_name,
            name,
            self.email_input.text(),
            self.phone_input.text(),
            self.cargo_input.text(),
            self.address_input.text(),
            self.photo_bytes  # envia foto
        )
        self.accept()

# ========== DIALOG VIEW FUNCIONÁRIO ====================================

class ViewFuncionarioDialog(QDialog):
    def __init__(self, company_name, funcionario):
        super().__init__()
        self.company_name = company_name
        self.funcionario = funcionario

        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Detalhes do Funcionário")
        self.setFixedWidth(480)
        self.setFixedHeight(300)

        form = QFormLayout()

        form.addRow("Nome:", QLabel(funcionario[1]))
        form.addRow("Email:", QLabel(funcionario[2]))
        form.addRow("Telefone:", QLabel(funcionario[3]))
        form.addRow("Cargo:", QLabel(funcionario[4]))
        form.addRow("Endereço:", QLabel(funcionario[5]))

        form.addRow("Foto:", QLabel())
        photo_label = form.itemAt(form.rowCount()-1, QFormLayout.FieldRole).widget()
        pixmap = QPixmap()
        if funcionario[6]:
            pixmap.loadFromData(funcionario[6])
        else:
            pixmap.load("assets/images/user_default.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        photo_label.setPixmap(pixmap)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        form.addWidget(btn_close)
        self.setLayout(form)

# ========== DIALOG EDIT FUNCIONÁRIO ====================================

class EditFuncionarioDialog(QDialog):
    def __init__(self, company_name, funcionario):
        super().__init__()
        self.company_name = company_name
        self.funcionario = funcionario
        self.photo_bytes = funcionario[6]  # foto atual

        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Editar Funcionário")
        self.setFixedWidth(400)

        form = QFormLayout()

        self.name_input = QLineEdit(funcionario[1])
        self.email_input = QLineEdit(funcionario[2])
        self.phone_input = QLineEdit(funcionario[3])
        self.cargo_input = QLineEdit(funcionario[4])
        self.address_input = QLineEdit(funcionario[5])

        # Foto
        self.photo_label = QLabel()
        pixmap = QPixmap()
        if self.photo_bytes:
            pixmap.loadFromData(self.photo_bytes)
        else:
            pixmap.load("assets/images/user_default.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo_label.setPixmap(pixmap)
        form.addRow("Foto:", self.photo_label)

        # Botão para trocar foto
        btn_change_photo = QPushButton("Alterar Foto")
        btn_change_photo.clicked.connect(self.change_photo)
        form.addWidget(btn_change_photo)

        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Cargo:", self.cargo_input)
        form.addRow("Endereço:", self.address_input)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)

        self.setLayout(form)

    def change_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
            with open(file_path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        ok = update_funcionario(
            self.company_name,
            self.funcionario[0],
            name=self.name_input.text(),
            email=self.email_input.text(),
            phone=self.phone_input.text(),
            cargo=self.cargo_input.text(),
            address=self.address_input.text(),
            photo_bytes=self.photo_bytes
        )
        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Nada para atualizar")

# ========== PÁGINA DE FUNCIONÁRIOS ==================================

class FuncionariosWindow(QWidget):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name

        self.setStyleSheet(CRUD_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        painel = QHBoxLayout()

        self.total_label = QLabel("Total de Funcionários: 0")
        btn_add = QPushButton("Adicionar Funcionário")
        btn_add.clicked.connect(self.open_add_dialog)

        painel.addWidget(self.total_label)
        painel.addStretch()
        painel.addWidget(btn_add)

        layout.addLayout(painel)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar funcionário...")
        self.search_input.textChanged.connect(self.search_funcionarios)

        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Nome", "Email", "Telefone", "Cargo", "Endereço", "Ações"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.refresh()

    def refresh(self, search=None):
        funcionarios = get_all_funcionarios(self.company_name)

        if search:
            s = search.lower()
            funcionarios = [f for f in funcionarios if s in f[1].lower()]

        self.total_label.setText(f"Total de Funcionários: {len(funcionarios)}")

        if len(funcionarios) == 0:
            self.table.hide()
            return

        self.table.show()
        self.table.setRowCount(len(funcionarios))

        for index, row in enumerate(funcionarios):
            _id, name, email, phone, cargo, address, photo_bytes = row  # agora 7 campos

            # Foto
            pixmap = QPixmap()
            if photo_bytes:
                pixmap.loadFromData(photo_bytes)
            else:
                pixmap.load("assets/images/user_default.png")
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            label_photo = QLabel()
            label_photo.setPixmap(pixmap)
            label_photo.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 0, label_photo)  # coluna 0 = foto

            # Outras colunas
            self.table.setItem(index, 1, QTableWidgetItem(name))
            self.table.setItem(index, 2, QTableWidgetItem(email))
            self.table.setItem(index, 3, QTableWidgetItem(phone))
            self.table.setItem(index, 4, QTableWidgetItem(cargo))
            self.table.setItem(index, 5, QTableWidgetItem(address))

            self.add_actions(index, _id)


    def add_actions(self, row, funcionario_id):

        btn_view = make_action_btn("Ver", "#f1c40f")
        btn_edit = make_action_btn("Editar", "#3498db")
        btn_delete = make_action_btn("Excluir", "#e74c3c")

        btn_view.setIcon(icon_eye())
        btn_edit.setIcon(icon_pencil())
        btn_delete.setIcon(icon_trash())

        btn_view.clicked.connect(lambda: self.view_funcionario(funcionario_id))
        btn_edit.clicked.connect(lambda: self.edit_funcionario(funcionario_id))
        btn_delete.clicked.connect(lambda: self.delete_funcionario_confirm(funcionario_id))

        hl = QHBoxLayout()
        hl.addWidget(btn_view)
        hl.addWidget(btn_edit)
        hl.addWidget(btn_delete)
        hl.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(hl)

        self.table.setCellWidget(row, 5, widget)

    def search_funcionarios(self):
        text = self.search_input.text()
        self.refresh(text)

    def open_add_dialog(self):
        dlg = AddFuncionarioDialog(self.company_name)
        if dlg.exec_():
            self.refresh()
    
    def view_funcionario(self, funcionario_id):
        funcionarios = get_all_funcionarios(self.company_name)
        funcionario = next((c for c in funcionarios if c[0]==funcionario_id), None)
        if not funcionario: return

        dlg = ViewFuncionarioDialog(self.company_name, funcionario)
        dlg.exec_()

    def edit_funcionario(self, funcionario_id):
        funcionarios = get_all_funcionarios(self.company_name)
        funcionario = next((c for c in funcionarios if c[0]==funcionario_id), None)
        if not funcionario: return

        dlg = EditFuncionarioDialog(self.company_name, funcionario)
        if dlg.exec_():
            self.refresh()

    def delete_funcionario_confirm(self, funcionario_id):
        verify = QMessageBox.question(
            self,
            "Excluir",
            "Tem certeza que deseja excluir este funcionário?",
            QMessageBox.Yes | QMessageBox.No
        )
        if verify == QMessageBox.Yes:
            delete_funcionario(self.company_name, funcionario_id)
            self.refresh()

# ========== ESTILO GLOBAL =====================================

CRUD_STYLE = """
    QWidget {
        background-color: #1b2330;
        color: #e5e5e5;
        font-size: 14px;
    }

    QLabel {
        color: #e5e5e5;
        font-weight: bold;
    }

    QPushButton {
        background-color: #3b6cee;
        padding: 8px 18px;
        border-radius: 6px;
        color: white;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #5580ff;
    }

    QPushButton:pressed {
        background-color: #2d59cc;
    }

    QLineEdit {
        border: 1px solid #3a4150;
        padding: 6px;
        border-radius: 5px;
        color: #eaeaea;
    }

    QTableWidget {
        background-color: #242c3b;
        border: 1px solid #384151;
        border-radius: 6px;
        gridline-color: #3c4558;
    }

    QHeaderView::section {
        background-color: #2e384a;
        padding: 6px;
        color: #d1d1d1;
        font-weight: bold;
        border: none;
    }

    QTableWidget QTableCornerButton::section {
        background-color: #2e384a;
        border: none;
    }

    QScrollBar:vertical {
        background: #202935;
        width: 10px;
    }
    QScrollBar::handle:vertical {
        background: #3b6cee;
        min-height: 20px;
        border-radius: 4px;
    }
"""