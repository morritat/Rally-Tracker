"""Декораторы для проверки JWT и ролей."""
from functools import wraps
from flask import request, jsonify
from backend.auth.jwt_helper import decode_token
from backend.database import Database


def login_required(f):
    """Требует авторизации."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Требуется авторизация'
            }), 401

        token = auth_header.split(' ', 1)[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Неверный или истёкший токен'
            }), 401

        db = Database()
        user = db.fetch_one(
            'SELECT id, email, full_name, role, is_blocked FROM users WHERE id = ?',
            (payload['userId'],)
        )
        if not user or user['is_blocked']:
            return jsonify({
                'success': False,
                'message': 'Аккаунт заблокирован или не найден'
            }), 403

        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Требует конкретную роль."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({
                    'success': False,
                    'message': 'Требуется авторизация'
                }), 401
            if request.current_user['role'] not in roles:
                return jsonify({
                    'success': False,
                    'message': f'Доступ запрещён. Требуется роль: {", ".join(roles)}'
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator