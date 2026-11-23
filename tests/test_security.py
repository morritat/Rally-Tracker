"""Тесты безопасности."""


class TestSQLInjection:
    def test_sql_injection_login(self, client):
        res = client.post('/api/auth/login', json={
            'email': "' OR '1'='1",
            'password': 'anything'
        })
        assert res.status_code == 401

    def test_sql_injection_register(self, client, db):
        res = client.post('/api/auth/register', json={
            'email': 'x@y.ru',
            'password': 'test123',
            'fullName': "test'; DROP TABLE users; --"
        })
        assert res.status_code in (201, 400)
        # Таблица users должна существовать
        check = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert check is not None


class TestJWT:
    def test_unauthorized_request(self, client):
        res = client.get('/api/stages/1')
        # Публичный эндпоинт — должен работать
        assert res.status_code == 200

    def test_protected_endpoint_without_token(self, client):
        res = client.post('/api/stages', json={'name': 'Test'})
        assert res.status_code == 401