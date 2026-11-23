"""Валидация пользовательских данных."""
import re


class Validator:
    EMAIL_PATTERN = re.compile(
        r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )
    NAME_PATTERN = re.compile(r'^[A-Za-zА-Яа-яЁё\s-]{2,150}$')

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        if not value:
            return ""
        cleaned = re.sub(r'[\x00-\x1f\x7f]', '', value)
        return cleaned[:max_length].strip()

    @staticmethod
    def validate_email(email: str) -> tuple:
        email = Validator.sanitize_string(email, 100)
        if not Validator.EMAIL_PATTERN.match(email):
            return False, "Некорректный email"
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple:
        if not password or len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        if len(password) > 128:
            return False, "Пароль слишком длинный"
        return True, ""

    @staticmethod
    def validate_full_name(name: str) -> tuple:
        name = Validator.sanitize_string(name, 150)
        if not Validator.NAME_PATTERN.match(name):
            return False, "Имя: от 2 до 150 символов, только буквы"
        return True, ""