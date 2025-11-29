import sqlite3

class LocalDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def execute(self, query, params=None):
        with self.conn:
            return self.conn.execute(query, params or [])
