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
    """Cria o DB isolado para a empresa com tabela users"""
    db_path = get_company_db_path(company_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            photo BLOB
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
