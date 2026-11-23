"""Маршруты регистрации и авторизации."""
from flask import Blueprint, request, jsonify
from backend.models.user import User
from backend.auth.jwt_helper import create_token
from backend.auth.decorators import login_required
from flask import request

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    user = User(
        email=(data.get('email') or '').strip().lower(),
        password=data.get('password') or '',
        full_name=(data.get('fullName') or '').strip(),
        role='user'
    )
    ok, result = user.save()
    if not ok:
        return jsonify({'success': False, 'message': result}), 400
    return jsonify({
        'success': True,
        'userId': result,
        'message': 'Регистрация успешна'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    user = User.authenticate(
        (data.get('email') or '').strip().lower(),
        data.get('password') or ''
    )
    if not user:
        return jsonify({
            'success': False,
            'message': 'Неверный email или пароль'
        }), 401

    token = create_token(user)
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'fullName': user['full_name'],
            'role': user['role']
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """Возвращает текущего пользователя для проверки сохранённой сессии на клиенте."""
    user = request.current_user
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'fullName': user['full_name'],
            'role': user['role']
        }
    }), 200
