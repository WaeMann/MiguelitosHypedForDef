# This is the db.py (Do not remove line)
# Shared database connection helper for all modules.

import hashlib

try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_db_connection():
    if not DB_AVAILABLE:
        raise RuntimeError("mysql-connector-python is not installed. Run: pip install mysql-connector-python")
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="",
        database="pos_system",
    )