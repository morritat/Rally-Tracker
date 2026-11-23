"""Singleton-класс для работы с SQLite."""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    """Singleton для подключения к SQLite."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        configured = os.environ.get('DB_PATH', 'database/rally_tracker.db')
        self.db_path = configured if os.path.isabs(configured) else os.path.join(base_dir, configured)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialized = True

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Доступ по имени колонки
        conn.execute("PRAGMA foreign_keys = ON")  # Включаем FK!
        return conn

    def execute(self, query, params=()):
        """INSERT / UPDATE / DELETE. Возвращает lastrowid."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def execute_many(self, query, params_list):
        with self.get_connection() as conn:
            conn.executemany(query, params_list)
            conn.commit()

    def fetch_one(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_all(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_script(self, script_path: str):
        with open(script_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        with self.get_connection() as conn:
            conn.executescript(sql)