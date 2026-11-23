"""Маршруты администрирования пользователей."""
from flask import Blueprint, request, jsonify
from backend.auth.decorators import login_required, require_role
from backend.database import Database
from backend.validators.validators import Validator

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@login_required
@require_role('admin')
def get_users():
    users = Database().fetch_all(
        'SELECT id, email, full_name, role, is_blocked, created_at FROM users ORDER BY id'
    )
    return jsonify({'success': True, 'users': users}), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@login_required
@require_role('admin')
def update_status(user_id):
    data = request.get_json(silent=True) or {}
    is_blocked = 1 if bool(data.get('is_blocked')) else 0
    target = Database().fetch_one('SELECT id, role FROM users WHERE id = ?', (user_id,))
    if not target:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    if target['role'] == 'admin':
        return jsonify({'success': False, 'message': 'Нельзя блокировать администраторов'}), 403
    if user_id == request.current_user['id'] and is_blocked:
        return jsonify({'success': False, 'message': 'Нельзя заблокировать самого себя'}), 400
    Database().execute(
        'UPDATE users SET is_blocked = ? WHERE id = ?', (is_blocked, user_id)
    )
    return jsonify({'success': True}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_user(user_id):
    if user_id == request.current_user['id']:
        return jsonify({'success': False, 'message': 'Нельзя удалить самого себя'}), 400
    db = Database()
    user = db.fetch_one('SELECT id, role FROM users WHERE id = ?', (user_id,))
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    if user['role'] == 'admin':
        return jsonify({'success': False, 'message': 'Удаление администратора запрещено'}), 403
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    return jsonify({'success': True}), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_role('admin')
def edit_user(user_id):
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    full_name = (data.get('full_name') or '').strip()
    role = (data.get('role') or 'user').strip()
    valid_email, email_msg = Validator.validate_email(email)
    valid_name, name_msg = Validator.validate_full_name(full_name)
    if not valid_email:
        return jsonify({'success': False, 'message': email_msg}), 400
    if not valid_name:
        return jsonify({'success': False, 'message': name_msg}), 400
    if role not in ('user', 'marshal'):
        return jsonify({'success': False, 'message': 'Допустимые роли: user или marshal'}), 400
    db = Database()
    target = db.fetch_one('SELECT id, role FROM users WHERE id = ?', (user_id,))
    if not target:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    if target['role'] == 'admin':
        return jsonify({'success': False, 'message': 'Редактирование администратора запрещено'}), 403
    duplicate = db.fetch_one('SELECT id FROM users WHERE email = ? AND id != ?', (email, user_id))
    if duplicate:
        return jsonify({'success': False, 'message': 'Email уже используется'}), 409
    db.execute('UPDATE users SET email = ?, full_name = ?, role = ? WHERE id = ?',
              (email, full_name, role, user_id))
    return jsonify({'success': True}), 200
