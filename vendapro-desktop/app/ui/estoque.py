from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QFrame, QMessageBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPainterPath, QPixmap, QColor
from app.database.user_repository import (
    get_all_stock, add_stock, get_product_by_search, update_product_quantity, update_stock, delete_stock
)

# ========== ICONES VETORIAIS (mesmo que antes) ==========

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

# ========== BOTÕES DE AÇÃO ==========

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


# ========== DIALOGS ==========
class ViewStockDialog(QDialog):
    def __init__(self, company_name, produto):
        super().__init__()
        self.setWindowTitle("Detalhes do Produto")
        self.setFixedSize(480,300)
        self.setStyleSheet(CRUD_STYLE)
        form = QFormLayout()
        for label, key in [("Nome","nome"),("Marca","marca"),("Valor Unitário","valor"),
                           ("Quantidade Atual","quantidade"),("Código de Barras","codigo_barra")]:
            form.addRow(label+":", QLabel(str(produto[key])))
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.close)
        form.addWidget(btn_close)
        self.setLayout(form)

class EditStockDialog(QDialog):
    def __init__(self, company_name, produto, refresh_callback=None):
        super().__init__()
        self.company_name = company_name
        self.produto = produto
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Editar Produto")
        self.setFixedWidth(400)
        self.setStyleSheet(CRUD_STYLE)

        form = QFormLayout()
        self.nome_input = QLineEdit(produto['nome'])
        self.marca_input = QLineEdit(produto['marca'])
        self.valor_input = QLineEdit(str(produto['valor']))
        self.qtd_input = QLineEdit(str(produto['quantidade']))
        self.codigo_barra_input = QLineEdit(produto['codigo_barra'])
        for label, widget in [("Nome", self.nome_input),("Marca", self.marca_input),
                              ("Valor Unitário", self.valor_input),("Quantidade Atual", self.qtd_input),
                              ("Código de Barras", self.codigo_barra_input)]:
            form.addRow(label+":", widget)
        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self.save)
        form.addWidget(btn_save)
        self.setLayout(form)

    def save(self):
        if not all([self.nome_input.text(), self.marca_input.text(), self.valor_input.text(),
                    self.qtd_input.text(), self.codigo_barra_input.text()]):
            QMessageBox.warning(self, "Erro", "Todos os campos são obrigatórios!")
            return
        update_stock(
            self.company_name,
            self.produto['id'],
            self.nome_input.text(),
            self.marca_input.text(),
            float(self.valor_input.text()),
            int(self.qtd_input.text()),
            self.codigo_barra_input.text()
        )
        if self.refresh_callback:
            self.refresh_callback()
        QMessageBox.information(self, "Sucesso", "Produto atualizado!")
        self.accept()

# ========== ESTOQUE WINDOW ==========
class EstoqueWindow(QWidget):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name
        self.setStyleSheet(CRUD_STYLE)
        layout = QVBoxLayout(); layout.setContentsMargins(15,15,15,15)

        # Botão Novo Movimento
        self.btn_new_mov = QPushButton("Novo Movimento")
        self.btn_new_mov.setStyleSheet("background-color:#28a745;color:white;padding:6px 12px;border-radius:4px;")
        self.btn_new_mov.clicked.connect(self.toggle_card)
        layout.addWidget(self.btn_new_mov)

        # Card de Movimentação (oculto)
        self.card = QFrame()
        self.card.setStyleSheet("background-color:#2e384a;border-radius:10px;padding:8px;")  # padding menor
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(5,5,5,5)  # margens menores
        card_layout.setSpacing(8)  # menos espaço entre widgets

        self.card_title = QLabel("Movimentação de Estoque")
        self.card_title.setStyleSheet("font-size:16px;font-weight:bold;")  # título menor
        card_layout.addWidget(self.card_title)

        # Pesquisa
        search_layout = QHBoxLayout()
        search_layout.setSpacing(2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto por nome, marca ou código de barras")
        btn_search = QPushButton("Buscar")
        btn_search.setStyleSheet("background-color:#3b6cee;color:white;padding:4px 8px;border-radius:4px;")  # padding menor
        self.search_input.returnPressed.connect(self.buscar_produto)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        card_layout.addLayout(search_layout)

        # Campos do produto
        self.nome_input = QLineEdit(); self.nome_input.setReadOnly(True)
        self.marca_input = QLineEdit(); self.marca_input.setReadOnly(True)
        self.valor_input = QLineEdit(); self.valor_input.setReadOnly(True)
        self.qtd_atual_input = QLineEdit(); self.qtd_atual_input.setReadOnly(True)
        for label, widget in [("Nome", self.nome_input), ("Marca", self.marca_input),
                            ("Valor Unitário", self.valor_input), ("Quantidade Atual", self.qtd_atual_input)]:
            lbl = QLabel(label+":"); lbl.setStyleSheet("font-size:13px;")  # fonte menor
            card_layout.addWidget(lbl)
            widget.setFixedHeight(30)  # altura menor dos QLineEdit
            card_layout.addWidget(widget)

        # Tipo movimento
        self.tipo_combo = QComboBox(); self.tipo_combo.addItems(["Entrada","Saída"]); self.tipo_combo.setFixedHeight(30)
        self.qtd_mov_input = QLineEdit(); self.qtd_mov_input.setPlaceholderText("Quantidade a movimentar"); self.qtd_mov_input.setFixedHeight(30)
        card_layout.addWidget(QLabel("Tipo de Movimento:")); card_layout.addWidget(self.tipo_combo)
        card_layout.addWidget(QLabel("Quantidade:")); card_layout.addWidget(self.qtd_mov_input)

        # Botão confirmar
        btn_confirm = QPushButton("Confirmar Movimento")
        btn_confirm.setStyleSheet("background-color:#2ecc71;color:white;padding:4px 8px;border-radius:4px;")  # menor
        btn_confirm.clicked.connect(self.confirmar_movimento)  # <<< ESSA LINHA
        card_layout.addWidget(btn_confirm)


        self.card.setLayout(card_layout)
        self.card.setVisible(False)
        layout.addWidget(self.card)


        # Tabela
        self.table = QTableWidget(); self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Produto","Marca","Código","Quantidade","Tipo","Origem","Data","Ações"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.produto_selecionado = None
        self.refresh_table(get_all_stock(self.company_name))

    # ========== MÉTODOS ==========
    def toggle_card(self):
        card_visivel = not self.card.isVisible()
        self.card.setVisible(card_visivel)
        self.table.setVisible(not card_visivel)
        if card_visivel:
            self.search_input.setFocus()  # coloca o cursor automaticamente

    def buscar_produto(self):
        termo = self.search_input.text().strip()
        if not termo: return
        produto = get_product_by_search(self.company_name, termo)
        if not produto:
            QMessageBox.warning(self, "Erro", "Produto não encontrado")
            return
        self.produto_selecionado = produto
        self.nome_input.setText(produto['nome'])
        self.marca_input.setText(produto['marca'])
        self.valor_input.setText(str(produto['valor']))
        self.qtd_atual_input.setText(str(produto['quantidade']))

    def confirmar_movimento(self):
        if not self.produto_selecionado: QMessageBox.warning(self, "Erro", "Busque e selecione um produto primeiro"); return
        qtd = int(self.qtd_mov_input.text()); tipo = self.tipo_combo.currentText()
        produto_id = self.produto_selecionado['id']; codigo_barra = self.produto_selecionado['codigo_barra']
        nova_qtd = self.produto_selecionado['quantidade'] + qtd if tipo=="Entrada" else self.produto_selecionado['quantidade'] - qtd
        if nova_qtd < 0: QMessageBox.warning(self,"Erro","Quantidade insuficiente em estoque"); return
        update_product_quantity(self.company_name, produto_id, nova_qtd)
        add_stock(self.company_name, produto_id, codigo_barra, qtd, tipo, origem="Interface")
        QMessageBox.information(self,"Sucesso","Movimento registrado!")
        self.qtd_atual_input.setText(str(nova_qtd))
        self.refresh_table(get_all_stock(self.company_name))
        self.card.setVisible(False)
        self.table.setVisible(True)  # tabela reaparece

    def refresh_table(self, movimentos):
        self.table.setRowCount(len(movimentos))
        for i, m in enumerate(movimentos):
            _id,nome,marca,codigo,qtd,tipo,origem,data = m
            self.table.setItem(i,0,QTableWidgetItem(nome))
            self.table.setItem(i,1,QTableWidgetItem(marca))
            self.table.setItem(i,2,QTableWidgetItem(codigo))
            self.table.setItem(i,3,QTableWidgetItem(str(qtd)))
            self.table.setItem(i,4,QTableWidgetItem(tipo))
            self.table.setItem(i,5,QTableWidgetItem(origem))
            self.table.setItem(i,6,QTableWidgetItem(data))
            # Botões ação
            self.add_actions(i, {'id':_id,'nome':nome,'marca':marca,'valor':0,'quantidade':qtd,'codigo_barra':codigo})

    def add_actions(self, row, produto):
        produto_id = produto['id']

        btn_view = make_action_btn("", "#f1c40f"); btn_view.setIcon(icon_eye())
        btn_edit = make_action_btn("", "#3498db"); btn_edit.setIcon(icon_pencil())
        btn_delete = make_action_btn("", "#e74c3c"); btn_delete.setIcon(icon_trash())
        btn_view.clicked.connect(lambda: self.view_stock_product(produto_id))
        btn_edit.clicked.connect(lambda: self.edit_stock_product(produto_id))
        btn_delete.clicked.connect(lambda: self.delete_product_confirm(produto_id))

        hl = QHBoxLayout()
        hl.addWidget(btn_view)
        hl.addWidget(btn_edit)
        hl.addWidget(btn_delete)
        hl.setContentsMargins(0,0,0,0)

        widget = QWidget()
        widget.setLayout(hl)
        self.table.setCellWidget(row,7,widget)

    def view_stock_product(self, produto_id):
        produto = get_product_by_search(self.company_name, produto_id)
        if not produto: return
        dlg = ViewStockDialog(self.company_name, produto); dlg.exec_()

    def edit_stock_product(self, produto_id):
        produto = get_product_by_search(self.company_name, produto_id)
        if not produto: return
        dlg = EditStockDialog(self.company_name, produto, refresh_callback=lambda: self.refresh_table(get_all_stock(self.company_name)))
        dlg.exec_()

    def delete_product_confirm(self, produto_id):
        verify = QMessageBox.question(self,"Excluir","Tem certeza que deseja excluir este produto?",QMessageBox.Yes|QMessageBox.No)
        if verify == QMessageBox.Yes:
            delete_stock(self.company_name, produto_id)
            self.refresh_table(get_all_stock(self.company_name))

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