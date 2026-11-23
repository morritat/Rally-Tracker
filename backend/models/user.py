"""Модель «Пользователь»."""
import bcrypt
from backend.models.base_model import BaseModel
from backend.database import Database  # ← ДОБАВИТЬ ЭТУ СТРОКУ
from backend.validators.validators import Validator


class User(BaseModel):
    table_name = "users"

    def __init__(self, email=None, password=None, full_name=None,
                 role='user', **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role = role

    def validate(self) -> tuple:
        checks = [
            Validator.validate_email(self.email),
            Validator.validate_password(self.password),
            Validator.validate_full_name(self.full_name),
        ]
        for ok, msg in checks:
            if not ok:
                return False, msg
        return True, ""

    def email_exists(self) -> bool:
        row = self.db.fetch_one(
            'SELECT id FROM users WHERE email = ?', (self.email,)
        )
        return row is not None

    def save(self) -> tuple:
        ok, msg = self.validate()
        if not ok:
            return False, msg
        if self.email_exists():
            return False, "Пользователь с таким email уже существует"

        password_hash = bcrypt.hashpw(
            self.password.encode('utf-8'),
            bcrypt.gensalt(rounds=10)
        ).decode('utf-8')

        user_id = self.db.execute(
            """INSERT INTO users (email, password_hash, full_name, role, is_blocked)
               VALUES (?, ?, ?, ?, 0)""",
            (self.email, password_hash, self.full_name, self.role)
        )
        self.id = user_id
        return True, user_id

    @staticmethod
    def authenticate(email: str, password: str) -> dict:
        db = Database()
        login = (email or '').strip()
        # Для администратора разрешён короткий логин 'admin'; в БД остаётся email.
        if login.lower() == 'admin':
            login = 'admin@rally.com'
        user = db.fetch_one(
            'SELECT * FROM users WHERE email = ?', (login,)
        )
        if not user:
            return None
        if user['is_blocked']:
            return None
        if bcrypt.checkpw(
            password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        ):
            return user
        return None