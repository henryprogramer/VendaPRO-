from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor, QImage

from app.database.user_repository import (
    create_fornecedor,
    get_all_fornecedores,
    update_fornecedor,
    delete_fornecedor
)

# ================== ICONES ==================
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

# ================== BOTÕES ==================
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

# ================== DIALOGS ==================
class AddFornDialog(QDialog):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.setWindowTitle("Novo Fornecedor")
        self.setStyleSheet(CRUD_STYLE)

        self.photo_data = None  # bytes da imagem

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.photo_label = QLabel("Nenhuma foto selecionada")
        self.btn_select_photo = QPushButton("Selecionar Foto")
        self.btn_select_photo.clicked.connect(self.select_photo)

        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Endereço:", self.address_input)
        form.addRow(self.btn_select_photo, self.photo_label)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)
        self.setLayout(form)

    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.bmp)")
        if path:
            pix = QPixmap(path).scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pix)
            # converter para bytes
            with open(path, "rb") as f:
                self.photo_data = f.read()

    def save(self):
        name = self.name_input.text()
        if not name:
            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
            return
        create_fornecedor(
            self.company_name,
            name,
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.photo_data
        )
        self.accept()

class ViewFornDialog(QDialog):
    def __init__(self, company_name, forn):
        super().__init__()
        self.company_name = company_name
        self.forn = forn
        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Detalhes do Fornecedor")
        self.setFixedSize(400,300)

        form = QFormLayout()
        form.addRow("Nome:", QLabel(forn[1]))
        form.addRow("Email:", QLabel(forn[2]))
        form.addRow("Telefone:", QLabel(forn[3]))
        form.addRow("Endereço:", QLabel(forn[4]))

        # foto
        photo_label = QLabel()
        if forn[5]:
            pix = QPixmap()
            pix.loadFromData(forn[5])
            pix = pix.scaled(100,100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            photo_label.setPixmap(pix)
        else:
            photo_label.setText("Sem foto")
        form.addRow("Foto:", photo_label)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        form.addWidget(btn_close)
        self.setLayout(form)

class EditFornDialog(QDialog):
    def __init__(self, company_name, forn):
        super().__init__()
        self.company_name = company_name
        self.forn = forn
        self.photo_data = forn[5]  # bytes existentes
        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Editar Fornecedor")
        self.setFixedWidth(400)

        form = QFormLayout()
        self.name_input = QLineEdit(forn[1])
        self.email_input = QLineEdit(forn[2])
        self.phone_input = QLineEdit(forn[3])
        self.address_input = QLineEdit(forn[4])
        self.photo_label = QLabel()
        if self.photo_data:
            pix = QPixmap()
            pix.loadFromData(self.photo_data)
            pix = pix.scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pix)
        else:
            self.photo_label.setText("Sem foto")
        self.btn_select_photo = QPushButton("Alterar Foto")
        self.btn_select_photo.clicked.connect(self.select_photo)

        form.addRow("Nome:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefone:", self.phone_input)
        form.addRow("Endereço:", self.address_input)
        form.addRow(self.btn_select_photo, self.photo_label)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)
        self.setLayout(form)

    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.bmp)")
        if path:
            pix = QPixmap(path).scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pix)
            with open(path, "rb") as f:
                self.photo_data = f.read()

    def save(self):
        ok = update_fornecedor(
            self.company_name,
            self.forn[0],
            self.name_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
            self.address_input.text(),
            self.photo_data
        )
        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Nada para atualizar")

# ================== TELA PRINCIPAL ==================
class FornecedoresWindow(QWidget):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.setStyleSheet(CRUD_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(15,15,15,15)

        # topo
        painel = QHBoxLayout()
        self.total_label = QLabel("Total de Fornecedores: 0")
        btn_add = QPushButton("Adicionar Fornecedor")
        btn_add.clicked.connect(self.open_add_dialog)
        painel.addWidget(self.total_label)
        painel.addStretch()
        painel.addWidget(btn_add)
        layout.addLayout(painel)

        # pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar fornecedor...")
        self.search_input.textChanged.connect(self.search_forns)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Foto","Nome","Email","Telefone","Endereço","Ações"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.refresh()

    def refresh(self, search=None):
        fornecedores = get_all_fornecedores(self.company_name)
        if search:
            s = search.lower()
            fornecedores = [c for c in fornecedores if s in c[1].lower()]

        self.total_label.setText(f"Total de Fornecedores: {len(fornecedores)}")
        if len(fornecedores)==0:
            self.table.hide()
            return
        self.table.show()
        self.table.setRowCount(len(fornecedores))

        for index, row in enumerate(fornecedores):
            _id, name, email, phone, address, photo = row
            # foto
            if photo:
                pix = QPixmap()
                pix.loadFromData(photo)
                pix = pix.scaled(50,50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_photo = QLabel()
                lbl_photo.setPixmap(pix)
                lbl_photo.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(index, 0, lbl_photo)
            else:
                self.table.setItem(index,0,QTableWidgetItem("Sem foto"))

            self.table.setItem(index,1,QTableWidgetItem(name))
            self.table.setItem(index,2,QTableWidgetItem(email))
            self.table.setItem(index,3,QTableWidgetItem(phone))
            self.table.setItem(index,4,QTableWidgetItem(address))

            self.add_actions(index,_id)

    def add_actions(self, row, forn_id):
        btn_view = make_action_btn("Ver","#f1c40f")
        btn_edit = make_action_btn("Editar","#3498db")
        btn_delete = make_action_btn("Excluir","#e74c3c")

        btn_view.setIcon(icon_eye())
        btn_edit.setIcon(icon_pencil())
        btn_delete.setIcon(icon_trash())

        btn_view.clicked.connect(lambda: self.view_forn(forn_id))
        btn_edit.clicked.connect(lambda: self.edit_forn(forn_id))
        btn_delete.clicked.connect(lambda: self.delete_forn_confirm(forn_id))

        hl = QHBoxLayout()
        hl.addWidget(btn_view)
        hl.addWidget(btn_edit)
        hl.addWidget(btn_delete)
        hl.setContentsMargins(0,0,0,0)

        widget = QWidget()
        widget.setLayout(hl)
        self.table.setCellWidget(row,5,widget)

    def search_forns(self):
        self.refresh(self.search_input.text())

    def open_add_dialog(self):
        dlg = AddFornDialog(self.company_name)
        if dlg.exec_():
            self.refresh()

    def view_forn(self, forn_id):
        forns = get_all_fornecedores(self.company_name)
        forn = next((f for f in forns if f[0]==forn_id), None)
        if not forn: return
        dlg = ViewFornDialog(self.company_name, forn)
        dlg.exec_()

    def edit_forn(self, forn_id):
        forns = get_all_fornecedores(self.company_name)
        forn = next((f for f in forns if f[0]==forn_id), None)
        if not forn: return
        dlg = EditFornDialog(self.company_name, forn)
        if dlg.exec_():
            self.refresh()

    def delete_forn_confirm(self, forn_id):
        verify = QMessageBox.question(self,"Excluir","Tem certeza que deseja excluir este fornecedor?",QMessageBox.Yes|QMessageBox.No)
        if verify==QMessageBox.Yes:
            delete_fornecedor(self.company_name, forn_id)
            self.refresh() 

# ================== ESTILO ==================
CRUD_STYLE = """
QWidget { background-color: #1b2330; color: #e5e5e5; font-size:14px; }
QLabel { color:#e5e5e5; font-weight:bold; }
QPushButton { background-color:#3b6cee; padding:8px 18px; border-radius:6px; color:white; font-weight:bold; }
QPushButton:hover { background-color:#5580ff; }
QPushButton:pressed { background-color:#2d59cc; }
QLineEdit { border:1px solid #3a4150; padding:6px; border-radius:5px; color:#eaeaea; }
QTableWidget { background-color:#242c3b; border:1px solid #384151; border-radius:6px; gridline-color:#3c4558; }
QHeaderView::section { background-color:#2e384a; padding:6px; color:#d1d1d1; font-weight:bold; border:none; }
QTableWidget QTableCornerButton::section { background-color:#2e384a; border:none; }
QScrollBar:vertical { background:#202935; width:10px; }
QScrollBar::handle:vertical { background:#3b6cee; min-height:20px; border-radius:4px; }
"""
