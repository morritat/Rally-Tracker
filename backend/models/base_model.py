"""Базовый класс для всех моделей."""
from backend.database import Database


class BaseModel:
    table_name = None

    def __init__(self, **kwargs):
        self.db = Database()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        raise NotImplementedError

    @classmethod
    def get_all(cls):
        db = Database()
        return db.fetch_all(f'SELECT * FROM {cls.table_name}')

    @classmethod
    def get_by_id(cls, record_id: int):
        db = Database()
        return db.fetch_one(
            f'SELECT * FROM {cls.table_name} WHERE id = ?',
            (record_id,)
        )

    @classmethod
    def delete(cls, record_id: int) -> bool:
        db = Database()
        db.execute(f'DELETE FROM {cls.table_name} WHERE id = ?', (record_id,))
        return True