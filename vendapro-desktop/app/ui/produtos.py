from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor

from app.database.user_repository import (
    get_all_products,
    create_product,
    update_product,
    delete_product
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

# ========== DIALOG ADD PRODUTO ====================================

from PyQt5.QtWidgets import QFileDialog

class AddProductDialog(QDialog):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.photo_bytes = None
        self.setWindowTitle("Novo Produto")
        self.setStyleSheet(CRUD_STYLE)

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.value_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.code_input = QLineEdit()

        form.addRow("Nome:", self.name_input)
        form.addRow("Valor:", self.value_input)
        form.addRow("Quantidade:", self.quantity_input)
        form.addRow("Marca:", self.brand_input)
        form.addRow("Código de Barra:", self.code_input)

        # Upload foto
        self.photo_label = QLabel()
        pixmap = QPixmap("assets/images/user_default.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo_label.setPixmap(pixmap)
        form.addRow("Foto:", self.photo_label)

        btn_photo = QPushButton("Selecionar Foto")
        btn_photo.clicked.connect(self.select_photo)
        form.addWidget(btn_photo)

        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)

        self.setLayout(form)

    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Escolher Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)

            # Carrega bytes da imagem pra salvar no banco
            with open(file_path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        #Aqui você chamaria create_product (ou equivalente) passando self.photo_bytes
        
        create_product(
            self.company_name,
            self.name_input.text(),
            self.value_input.text(),
            self.quantity_input.text(),
            self.brand_input.text(),
            self.code_input.text(),
            self.photo_bytes
        )
        self.accept()


    def select_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.bmp)")
        if path:
            pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
            with open(path, "rb") as f:
                self.photo_bytes = f.read()

    def save(self):
        if not self.name_input.text():
            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
            return
        create_product(
            self.company_name,
            self.name_input.text(),
            float(self.value_input.text() or 0),
            int(self.quantity_input.text() or 0),
            self.brand_input.text(),
            self.code_input.text(),
            self.photo_bytes
        )
        self.accept()

# ========== DIALOG VIEW PRODUTO ====================================

class ViewProductDialog(QDialog):
    def __init__(self, company_name, product):
        super().__init__()
        self.company_name = company_name
        self.product = product
        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Detalhes do Produto")
        self.setFixedWidth(480)
        self.setFixedHeight(350)

        form = QFormLayout()
        form.addRow("Nome:", QLabel(product[1]))
        form.addRow("Valor:", QLabel(str(product[2])))
        form.addRow("Quantidade:", QLabel(str(product[3])))
        form.addRow("Marca:", QLabel(product[4]))
        form.addRow("Código de Barra:", QLabel(product[5]))

        photo_label = QLabel()
        pixmap = QPixmap()
        if product[6]:
            pixmap.loadFromData(product[6])
        else:
            pixmap.load("assets/images/user_default.png")
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        photo_label.setPixmap(pixmap)
        form.addRow("Foto:", photo_label)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        form.addWidget(btn_close)
        self.setLayout(form)

# ========== DIALOG EDIT PRODUTO ====================================

class EditProductDialog(QDialog):
    def __init__(self, company_name, product):
        super().__init__()
        self.company_name = company_name
        self.product = product
        self.photo_bytes = product[6]
        self.setStyleSheet(CRUD_STYLE)
        self.setWindowTitle("Editar Produto")
        self.setFixedWidth(400)

        form = QFormLayout()
        self.name_input = QLineEdit(product[1])
        self.value_input = QLineEdit(str(product[2]))
        self.quantity_input = QLineEdit(str(product[3]))
        self.brand_input = QLineEdit(product[4])
        self.code_input = QLineEdit(product[5])

        form.addRow("Nome:", self.name_input)
        form.addRow("Valor:", self.value_input)
        form.addRow("Quantidade:", self.quantity_input)
        form.addRow("Marca:", self.brand_input)
        form.addRow("Código de Barra:", self.code_input)

        self.photo_label = QLabel()
        pixmap = QPixmap()
        if product[6]:
            pixmap.loadFromData(product[6])
        else:
            pixmap.load("assets/images/user_default.png")
        self.photo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))

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
        ok = update_product(
            self.company_name,
            self.product[0],
            self.name_input.text(),
            float(self.value_input.text() or 0),
            int(self.quantity_input.text() or 0),
            self.brand_input.text(),
            self.code_input.text(),
            self.photo_bytes
        )
        if ok:
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Nada para atualizar")

# ========== PÁGINA DE PRODUTOS ==================================

class ProdutosWindow(QWidget):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.setStyleSheet(CRUD_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        painel = QHBoxLayout()
        self.total_label = QLabel("Total de Produtos: 0")
        btn_add = QPushButton("Adicionar Produto")
        btn_add.clicked.connect(self.open_add_dialog)
        painel.addWidget(self.total_label)
        painel.addStretch()
        painel.addWidget(btn_add)
        layout.addLayout(painel)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Foto", "Nome", "Valor", "Quantidade", "Marca", "Código", "Ações"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.refresh()

    def refresh(self, search=None):
        produtos = get_all_products(self.company_name)
        if search:
            s = search.lower()
            produtos = [p for p in produtos if s in p[1].lower()]

        self.total_label.setText(f"Total de Produtos: {len(produtos)}")
        if len(produtos) == 0:
            self.table.hide()
            return
        self.table.show()
        self.table.setRowCount(len(produtos))

        for index, row in enumerate(produtos):
            _id, name, value, quantity, brand, code, photo_bytes = row

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

            self.table.setItem(index, 1, QTableWidgetItem(name))
            self.table.setItem(index, 2, QTableWidgetItem(str(value)))
            self.table.setItem(index, 3, QTableWidgetItem(str(quantity)))
            self.table.setItem(index, 4, QTableWidgetItem(brand))
            self.table.setItem(index, 5, QTableWidgetItem(code))

            self.add_actions(index, _id)

    def add_actions(self, row, product_id):
        btn_view = make_action_btn("Ver", "#f1c40f")
        btn_edit = make_action_btn("Editar", "#3498db")
        btn_delete = make_action_btn("Excluir", "#e74c3c")
        btn_view.setIcon(icon_eye())
        btn_edit.setIcon(icon_pencil())
        btn_delete.setIcon(icon_trash())
        btn_view.clicked.connect(lambda: self.view_product(product_id))
        btn_edit.clicked.connect(lambda: self.edit_product(product_id))
        btn_delete.clicked.connect(lambda: self.delete_product_confirm(product_id))

        hl = QHBoxLayout()
        hl.addWidget(btn_view)
        hl.addWidget(btn_edit)
        hl.addWidget(btn_delete)
        hl.setContentsMargins(0,0,0,0)
        widget = QWidget()
        widget.setLayout(hl)
        self.table.setCellWidget(row, 6, widget)

    def search_products(self):
        self.refresh(self.search_input.text())

    def open_add_dialog(self):
        dialog = AddProductDialog(self.company_name)
        if dialog.exec_():
            self.refresh()

    def view_product(self, product_id):
        produtos = get_all_products(self.company_name)
        product = next((p for p in produtos if p[0]==product_id), None)
        if not product: return
        dlg = ViewProductDialog(self.company_name, product)
        dlg.exec_()

    def edit_product(self, product_id):
        produtos = get_all_products(self.company_name)
        product = next((p for p in produtos if p[0]==product_id), None)
        if not product: return
        dlg = EditProductDialog(self.company_name, product)
        if dlg.exec_():
            self.refresh()

    def delete_product_confirm(self, product_id):
        verify = QMessageBox.question(
            self,
            "Excluir",
            "Tem certeza que deseja excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )
        if verify == QMessageBox.Yes:
            delete_product(self.company_name, product_id)
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
QPushButton:hover { background-color: #5580ff; }
QPushButton:pressed { background-color: #2d59cc; }
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
