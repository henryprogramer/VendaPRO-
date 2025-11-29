import os

class Settings:
    DB_PATH = "db/vendapro.db"
    API_URL = os.getenv("API_URL", "http://localhost:8000")
