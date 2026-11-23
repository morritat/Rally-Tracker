"""Тесты авторизации."""


class TestRegister:
    def test_register_success(self, client):
        res = client.post('/api/auth/register', json={
            'email': 'test_new@rally.com',
            'password': '1987',
            'fullName': 'Test User'
        })
        assert res.status_code == 201
        assert res.get_json()['success'] is True

    def test_register_short_password(self, client):
        res = client.post('/api/auth/register', json={
            'email': 'test_short@rally.com',
            'password': '123',
            'fullName': 'Test User'
        })
        assert res.status_code == 400

    def test_register_invalid_email(self, client):
        res = client.post('/api/auth/register', json={
            'email': 'not-email',
            'password': '1987',
            'fullName': 'Test User'
        })
        assert res.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'user@rally.com',
            'password': '1987'
        })
        assert res.status_code == 200
        assert 'token' in res.get_json()

    def test_login_wrong_password(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'user@rally.com',
            'password': 'wrong'
        })
        assert res.status_code == 401

    def test_login_blocked_user(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'fan@rally.com',
            'password': '1987'
        })
        assert res.status_code == 401

    def test_register_persists_and_login_requires_explicit_action(self, client, db):
        db.execute('DELETE FROM users WHERE email = ?', ('persist_user@rally.com',))
        res = client.post('/api/auth/register', json={
            'email': 'persist_user@rally.com',
            'password': 'abc12345',
            'fullName': 'Persist User'
        })
        assert res.status_code == 201
        saved = db.fetch_one('SELECT email, full_name, password_hash FROM users WHERE email = ?',
                            ('persist_user@rally.com',))
        assert saved is not None
        assert saved['full_name'] == 'Persist User'
        assert saved['password_hash'] != 'abc12345'
        # Registration endpoint returns no auth token; login is a separate request.
        assert 'token' not in res.get_json()
        db.execute('DELETE FROM users WHERE email = ?', ('persist_user@rally.com',))


class TestCurrentUser:
    def test_me_requires_token(self, client):
        res = client.get('/api/auth/me')
        assert res.status_code == 401

    def test_me_returns_user_for_valid_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'user@rally.com',
            'password': '1987'
        })
        assert login.status_code == 200
        token = login.get_json()['token']
        res = client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['user']['email'] == 'user@rally.com'
