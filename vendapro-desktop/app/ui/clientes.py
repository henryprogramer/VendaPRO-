from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor

from app.database.user_repository import (
    get_all_clients,
    create_client,
    update_client,
    delete_client
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

# ========== BOTÕES DE AÇÃO ======================================

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

# ========== DIALOG ADD CLIENTE ====================================

class AddClientDialog(QDialog):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.photo_bytes = None  # guardar bytes da imagem
        self.setWindowTitle("Novo Cliente")
        self.setStyleSheet(CRUD_STYLE)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Endereço:", self.address_input)

        # botão para selecionar foto
        self.photo_label = QLabel()
        self.photo_label.setPixmap(QPixmap("assets/images/user_default.png").scaled(80,80))
        btn_photo = QPushButton("Selecionar Foto")
        btn_photo.clicked.connect(self.select_photo)
        form.addRow(btn_photo, self.photo_label)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)
        self.setLayout(form)

    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.bmp)")
        if path:
            pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
            with open(path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
            return

        create_client(
            self.company_name,
            name,
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.photo_bytes  # envia bytes da foto
        )
        self.accept()

# ========== DIALOG VER CLIENTE ====================================

class ViewClientDialog(QDialog):
    def __init__(self, company_name, client):
        super().__init__()
        self.company_name = company_name
        self.client = client   # tuple

        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Detalhes do Cliente")
        self.setFixedWidth(480)
        self.setFixedHeight(300)

        form = QFormLayout()

        form.addRow("Nome:", QLabel(client[1]))
        form.addRow("Email:", QLabel(client[2]))
        form.addRow("Telefone:", QLabel(client[3]))
        form.addRow("Endereço:", QLabel(client[4]))

        photo_label = QLabel()
        pixmap = QPixmap()
        if client[5]:
            pixmap.loadFromData(client[5])
        else:
            pixmap.load("assets/images/user_default.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        photo_label.setPixmap(pixmap)
        photo_label.setAlignment(Qt.AlignLeft)

        form.addRow("Foto:", photo_label)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        form.addWidget(btn_close)

        self.setLayout(form)


# ========== DIALOG EDIT CLIENTE ====================================

class EditClientDialog(QDialog):
    def __init__(self, company_name, client):
        super().__init__()
        self.company_name = company_name
        self.client = client
        self.photo_bytes = client[5]  # pega bytes atuais da foto

        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Editar Cliente")
        self.setFixedWidth(400)

        form = QFormLayout()

        self.name_input = QLineEdit(client[1])
        self.email_input = QLineEdit(client[2])
        self.phone_input = QLineEdit(client[3])
        self.address_input = QLineEdit(client[4])

        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Endereço:", self.address_input)

        # foto
        self.photo_label = QLabel()
        pixmap = QPixmap()
        if self.photo_bytes:
            pixmap.loadFromData(self.photo_bytes)
        else:
            pixmap.load("assets/images/user_default.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo_label.setPixmap(pixmap)
        self.photo_label.setAlignment(Qt.AlignLeft)

        btn_photo = QPushButton("Selecionar Foto")
        btn_photo.clicked.connect(self.select_photo)
        form.addRow(btn_photo, self.photo_label)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)

        self.setLayout(form)

    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.bmp)")
        if path:
            pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
            with open(path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        ok = update_client(
            self.company_name,
            self.client[0],
            self.name_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.photo_bytes  # envia bytes da foto atualizada
        )
        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Nada para atualizar")

# ========== PÁGINA DE CLIENTES ==================================

class ClientesWindow(QWidget):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.setStyleSheet(CRUD_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # topo
        painel = QHBoxLayout()
        self.total_label = QLabel("Total de Clientes: 0")
        btn_add = QPushButton("Adicionar Cliente")
        btn_add.clicked.connect(self.open_add_dialog)
        painel.addWidget(self.total_label)
        painel.addStretch()
        painel.addWidget(btn_add)
        layout.addLayout(painel)

        # search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente...")
        self.search_input.textChanged.connect(self.search_clients)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Foto", "Nome", "Email", "Telefone", "Endereço", "Ações"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.refresh()

    def refresh(self, search=None):
        clientes = get_all_clients(self.company_name)
        if search:
            s = search.lower()
            clientes = [c for c in clientes if s in c[1].lower()]

        self.total_label.setText(f"Total de Clientes: {len(clientes)}")
        if not clientes:
            self.table.hide()
            return

        self.table.show()
        self.table.setRowCount(len(clientes))

        for index, row in enumerate(clientes):
            _id, name, email, phone, address, photo_bytes = row

            # foto
            pixmap = QPixmap()
            if photo_bytes:
                pixmap.loadFromData(photo_bytes)
            else:
                pixmap.load("assets/images/user_default.png")
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label_photo = QLabel()
            label_photo.setPixmap(pixmap)
            label_photo.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(index, 0, label_photo)

            # outras colunas
            self.table.setItem(index, 1, QTableWidgetItem(name))
            self.table.setItem(index, 2, QTableWidgetItem(email))
            self.table.setItem(index, 3, QTableWidgetItem(phone))
            self.table.setItem(index, 4, QTableWidgetItem(address))

            self.add_actions(index, _id)

    def add_actions(self, row, client_id):
        btn_view = make_action_btn("Ver", "#f1c40f")
        btn_edit = make_action_btn("Editar", "#3498db")
        btn_delete = make_action_btn("Excluir", "#e74c3c")
        btn_view.setIcon(icon_eye())
        btn_edit.setIcon(icon_pencil())
        btn_delete.setIcon(icon_trash())

        btn_view.clicked.connect(lambda: self.view_client(client_id))
        btn_edit.clicked.connect(lambda: self.edit_client(client_id))
        btn_delete.clicked.connect(lambda: self.delete_client_confirm(client_id))

        hl = QHBoxLayout()
        hl.addWidget(btn_view)
        hl.addWidget(btn_edit)
        hl.addWidget(btn_delete)
        hl.setContentsMargins(0, 0, 0, 0)

        widget = QWidget()
        widget.setLayout(hl)
        self.table.setCellWidget(row, 5, widget)

    def search_clients(self):
        self.refresh(self.search_input.text())

    def open_add_dialog(self):
        dialog = AddClientDialog(self.company_name)
        if dialog.exec_():
            self.refresh()

    def view_client(self, client_id):
        clients = get_all_clients(self.company_name)
        client = next((c for c in clients if c[0] == client_id), None)
        if client:
            dlg = ViewClientDialog(self.company_name, client)
            dlg.exec_()

    def edit_client(self, client_id):
        clients = get_all_clients(self.company_name)
        client = next((c for c in clients if c[0] == client_id), None)
        if client:
            dlg = EditClientDialog(self.company_name, client)
            if dlg.exec_():
                self.refresh()

    def delete_client_confirm(self, client_id):
        verify = QMessageBox.question(
            self,
            "Excluir",
            "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        if verify == QMessageBox.Yes:
            delete_client(self.company_name, client_id)
            self.refresh()

# ========== ESTILO GLOBAL =====================================

CRUD_STYLE = """
    QWidget { background-color: #1b2330; color: #e5e5e5; font-size: 14px; }
    QLabel { color: #e5e5e5; font-weight: bold; }
    QPushButton { background-color: #3b6cee; padding: 8px 18px; border-radius: 6px; color: white; font-weight: bold; }
    QPushButton:hover { background-color: #5580ff; }
    QPushButton:pressed { background-color: #2d59cc; }
    QLineEdit { border: 1px solid #3a4150; padding: 6px; border-radius: 5px; color: #eaeaea; }
    QTableWidget { background-color: #242c3b; border: 1px solid #384151; border-radius: 6px; gridline-color: #3c4558; }
    QHeaderView::section { background-color: #2e384a; padding: 6px; color: #d1d1d1; font-weight: bold; border: none; }
    QTableWidget QTableCornerButton::section { background-color: #2e384a; border: none; }
    QScrollBar:vertical { background: #202935; width: 10px; }
    QScrollBar::handle:vertical { background: #3b6cee; min-height: 20px; border-radius: 4px; }
"""
