"""Генерация и проверка JWT-токенов."""
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('JWT_SECRET', 'dev-secret')
EXPIRES_HOURS = int(os.environ.get('JWT_EXPIRES_IN_HOURS', 24))


def create_token(user: dict) -> str:
    payload = {
        'userId': user['id'],
        'role': user['role'],
        'email': user['email'],
        'exp': datetime.utcnow() + timedelta(hours=EXPIRES_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None