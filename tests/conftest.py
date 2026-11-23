"""Фикстуры для тестов."""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app as flask_app
from backend.database import Database


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db():
    return Database()


@pytest.fixture
def auth_headers(client):
    """Получить JWT-токен для тестового пользователя."""
    client.post('/api/auth/login', json={
        'email': 'user@rally.com',
        'password': '1987'
    })
    res = client.post('/api/auth/login', json={
        'email': 'user@rally.com',
        'password': '1987'
    })
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client):
    res = client.post('/api/auth/login', json={
        'email': 'admin@rally.com',
        'password': '1987'
    })
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}