import sqlite3
import hashlib

DB_PATH = "database.db"

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_login(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    saved_hash = result[0]
    return saved_hash == hash_password(password)
