import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GLOBAL_DB = os.path.join(BASE_DIR, "database.db")  # banco global para registrar empresas

# ------------------- UTIL -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection(db_path=GLOBAL_DB):
    return sqlite3.connect(db_path)

# ------------------- INICIALIZAÇÃO -------------------
def init_db():
    """Banco global apenas para companies (empresa + logo)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            logo BLOB
        )
    """)
    conn.commit()
    conn.close()

def get_company_db_path(company_name):
    safe_name = company_name.lower().replace(" ", "_")
    return os.path.join(BASE_DIR, f"{safe_name}.db")

def init_company_db(company_name):
    db_path = get_company_db_path(company_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ⭐ NOVA TABELA USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            photo BLOB
        )
    """) 

    # ⭐ NOVA TABELA CLIENTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            photo BLOB
        )
    """)

    # ⭐ NOVA TABELA FUNCIONÁRIOS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            cargo TEXT,
            address TEXT,
            photo BLOB
        )
    """)

    # ⭐ NOVA TABELA FORNECEDORES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            photo BLOB
        )
    """)

    # ⭐ NOVA TABELA PRODUTOS
    cursor.execute("""
        CREATE TABLE produto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            marca TEXT NOT NULL,
            codigo_barra TEXT UNIQUE NOT NULL,
            photo BLOB
        )
    """)

    # ⭐ NOVA TABELA ESTOQUE
    cursor.execute("""
        CREATE TABLE estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            codigo_barra TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            movimento_tipo TEXT NOT NULL,  
            origem TEXT NOT NULL,         
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(produto_id) REFERENCES produto(id)
        )
    """)

    conn.commit()
    conn.close()
    return db_path
 
# ------------------- EMPRESA -------------------
def create_company(name, logo_bytes=None):
    """Cria empresa global + DB isolado"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO companies (name, logo) VALUES (?, ?)", (name, logo_bytes))
        conn.commit()
        company_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return None  # empresa já existe
    conn.close()

    # inicializa DB isolado da empresa
    init_company_db(name)
    return company_id

def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies ORDER BY name")
    companies = cursor.fetchall()
    conn.close()
    return companies

def get_company_logo(company_name):
    """Retorna bytes da logo da empresa"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT logo FROM companies WHERE name = ?", (company_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# ------------------- USUÁRIO -------------------
def create_user(company_name, username, password, photo_bytes=None):
    """Cria usuário dentro do DB da empresa"""
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, photo) VALUES (?, ?, ?)",
            (username, hash_password(password), photo_bytes)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_id(company_name, user_id):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)  # conecta no DB certo
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, photo FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "photo": row[2],
            "company_name": company_name
        }
    return None

# ------------------- CLIENTES -------------------
def create_client(company_name, name, email, phone, address, photo_bytes=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (name, email, phone, address, photo)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, phone, address, photo_bytes))
    conn.commit()
    conn.close()

def get_all_clients(company_name):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_client(company_name, client_id, name=None, email=None, phone=None, address=None, photo=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    fields = []
    params = []

    if name:
        fields.append("name=?")
        params.append(name)
    if email:
        fields.append("email=?")
        params.append(email)
    if phone:
        fields.append("phone=?")
        params.append(phone)
    if address:
        fields.append("address=?")
        params.append(address)
    if photo:
        fields.append("photo=?")
        params.append(photo)

    if not fields:
        conn.close()
        return False  # nada pra atualizar

    params.append(client_id)
    sql = f"UPDATE clients SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return True


def delete_client(company_name, client_id):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
 
# ------------------- FUNCIONÁRIOS -------------------
def create_funcionario(company_name, name, email, phone, cargo, address, photo_bytes=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO funcionarios (name, email, phone, cargo, address, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, phone, cargo, address, photo_bytes))
    conn.commit()
    conn.close()

def get_all_funcionarios(company_name):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM funcionarios ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_funcionario(company_name, funcionario_id, name=None, email=None, phone=None, cargo=None, address=None, photo_bytes=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    fields = []
    params = []

    if name:
        fields.append("name=?")
        params.append(name)
    if email:
        fields.append("email=?")
        params.append(email)
    if phone:
        fields.append("phone=?")
        params.append(phone)
    if cargo:
        fields.append("cargo=?")
        params.append(cargo)
    if address:
        fields.append("address=?")
        params.append(address)
    if photo_bytes is not None:  # permite atualizar a foto
        fields.append("photo=?")
        params.append(photo_bytes)

    if not fields:
        conn.close()
        return False

    params.append(funcionario_id)
    sql = f"UPDATE funcionarios SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return True


def delete_funcionario(company_name, funcionario_id):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM funcionarios WHERE id=?", (funcionario_id,))
    conn.commit()
    conn.close()

# ------------------- FORNECCEDORES -------------------
def create_fornecedor(company_name, name, email, phone, address, photo_bytes=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fornecedores (name, email, phone, address, photo)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, phone, address, photo_bytes))
    conn.commit()
    conn.close()

def get_all_fornecedores(company_name):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fornecedores ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_fornecedor(company_name, forn_id, name=None, email=None, phone=None, address=None, photo=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    fields = []
    params = []

    if name:
        fields.append("name=?")
        params.append(name)
    if email:
        fields.append("email=?")
        params.append(email)
    if phone:
        fields.append("phone=?")
        params.append(phone)
    if address:
        fields.append("address=?")
        params.append(address)
    if photo:
        fields.append("photo=?")
        params.append(photo)

    if not fields:
        conn.close()
        return False  # nada pra atualizar

    params.append(forn_id)
    sql = f"UPDATE fornecedores SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()
    return True


def delete_fornecedor(company_name, client_id):

    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fornecedores WHERE id=?", (client_id,))
    conn.commit()
    conn.close()

# ------------------- PRODUTOS -------------------
def create_product(company_name, nome, valor, quantidade, marca, codigo_barra, photo_bytes=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produto (nome, valor, quantidade, marca, codigo_barra, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, valor, quantidade, marca, codigo_barra, photo_bytes))
    conn.commit()
    conn.close()


def get_all_products(company_name):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produto ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_product(company_name, product_id, nome=None, valor=None, quantidade=None, marca=None, codigo_barra=None, photo=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    fields = []
    params = []

    if nome is not None:
        fields.append("nome=?")
        params.append(nome)

    if valor is not None:
        fields.append("valor=?")
        params.append(valor)

    if quantidade is not None:
        fields.append("quantidade=?")
        params.append(quantidade)

    if marca is not None:
        fields.append("marca=?")
        params.append(marca)

    if codigo_barra is not None:
        fields.append("codigo_barra=?")
        params.append(codigo_barra)

    if photo is not None:
        fields.append("photo=?")
        params.append(photo)

    if not fields:
        conn.close()
        return False  # nada pra atualizar

    params.append(product_id)

    sql = f"UPDATE produto SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, params)

    conn.commit()
    conn.close()
    return True


def delete_product(company_name, product_id):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produto WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    

def get_product_by_search(company_name, termo):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    like_term = f"%{termo}%"
    cursor.execute("""
        SELECT id, nome, marca, valor, quantidade, codigo_barra
        FROM produto
        WHERE nome LIKE ? OR marca LIKE ? OR codigo_barra LIKE ?
        LIMIT 1
    """, (like_term, like_term, like_term))
    
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'nome': row[1],
            'marca': row[2],
            'valor': row[3],
            'quantidade': row[4],
            'codigo_barra': row[5]
        }
    return None

def update_product_quantity(company_name, product_id, nova_qtd):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE produto
        SET quantidade = ?
        WHERE id = ?
    """, (nova_qtd, product_id))
    
    conn.commit()
    conn.close()


# ------------------- ESTOQUE -------------------
def add_stock(company_name, produto_id, codigo_barra, quantidade, movimento_tipo, origem):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO estoque (produto_id, codigo_barra, quantidade, movimento_tipo, origem)
        VALUES (?, ?, ?, ?, ?)
    """, (produto_id, codigo_barra, quantidade, movimento_tipo, origem))

    conn.commit()
    conn.close()

def get_all_stock(company_name):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, p.nome, p.marca, e.codigo_barra, e.quantidade, e.movimento_tipo, e.origem, e.data
        FROM estoque e
        JOIN produto p ON e.produto_id = p.id
        ORDER BY e.data DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_stock(company_name, stock_id, quantidade=None, movimento_tipo=None, origem=None):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    fields = []
    params = []

    if quantidade is not None:
        fields.append("quantidade=?")
        params.append(quantidade)
    if movimento_tipo is not None:
        fields.append("movimento_tipo=?")
        params.append(movimento_tipo)
    if origem is not None:
        fields.append("origem=?")
        params.append(origem)

    if not fields:
        conn.close()
        return False  # nada pra atualizar

    params.append(stock_id)
    sql = f"UPDATE estoque SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, params)

    conn.commit()
    conn.close()
    return True

def delete_stock(company_name, stock_id):
    db_path = get_company_db_path(company_name)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estoque WHERE id=?", (stock_id,))
    conn.commit()
    conn.close()

# ------------------- VALIDAR LOGIN -------------------
def validate_login_for_company(company_name, username, password):
    db_path = get_company_db_path(company_name)
    if not os.path.exists(db_path):
        return False

    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    uid, uname, stored_hash = row
    if stored_hash != hash_password(password):
        return False

    # pega logo da empresa
    logo_bytes = get_company_logo(company_name)

    return {
        "id": uid,
        "username": uname,
        "company_name": company_name,
        "company_logo": logo_bytes
    }

# ------------------- INICIALIZAÇÃO -------------------
init_db()
