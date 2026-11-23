"""Маршруты этапов (СУ)."""
from flask import Blueprint, request, jsonify
from backend.models.stage import Stage
from backend.services.weather_service import WeatherService
from backend.auth.decorators import login_required, require_role

stage_bp = Blueprint('stages', __name__, url_prefix='/api/stages')


@stage_bp.route('', methods=['GET'])
def get_stages():
    """Публичный список этапов."""
    stages = Stage.get_all_with_weather()
    return jsonify({'success': True, 'stages': stages}), 200


@stage_bp.route('/weather/karelia', methods=['GET'])
def get_karelia_weather():
    """Текущая погода в Карелии (Петрозаводск как региональная точка)."""
    weather = WeatherService.get_weather(61.7849, 34.3469)
    if not weather:
        return jsonify({
            'success': False,
            'message': 'Погода временно недоступна'
        }), 503
    return jsonify({
        'success': True,
        'location': 'Петрозаводск, Карелия',
        'weather': weather
    }), 200


@stage_bp.route('/<int:stage_id>/weather-current', methods=['GET'])
def get_stage_current_weather(stage_id):
    stage = Stage.get_by_id(stage_id)
    if not stage:
        return jsonify({'success': False, 'message': 'Этап не найден'}), 404
    lat, lon = stage.get('latitude'), stage.get('longitude')
    if lat is None or lon is None:
        return jsonify({'success': False, 'message': 'Для этапа не заданы координаты'}), 503
    weather = WeatherService.get_weather(lat, lon)
    if not weather:
        return jsonify({'success': False, 'message': 'Погода временно недоступна'}), 503
    return jsonify({'success': True, 'location': stage.get('location') or stage.get('name'), 'weather': weather}), 200


@stage_bp.route('/<int:stage_id>', methods=['GET'])
def get_stage(stage_id):
    """Один этап с деталями."""
    stage = Stage.get_by_id(stage_id)
    if not stage:
        return jsonify({'success': False, 'message': 'Этап не найден'}), 404
    return jsonify({'success': True, 'stage': stage}), 200


@stage_bp.route('', methods=['POST'])
@login_required
@require_role('marshal', 'admin')
def create_stage():
    """Создание этапа (погода подтянется автоматически)."""
    data = request.get_json()
    stage = Stage(
        name=data.get('name', '').strip(),
        date=data.get('date'),
        location=data.get('location', '').strip(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        distance_km=data.get('distance_km')
    )
    stage_id = stage.save()
    return jsonify({'success': True, 'stageId': stage_id}), 201


@stage_bp.route('/<int:stage_id>/weather', methods=['POST'])
@login_required
@require_role('marshal', 'admin')
def update_weather(stage_id):
    """Обновить погоду для этапа (вызов OpenWeatherMap)."""
    weather = Stage.update_weather(stage_id)
    if not weather:
        return jsonify({
            'success': False,
            'message': 'Не удалось получить погоду (нет координат или ошибка API)'
        }), 500
    return jsonify({'success': True, 'weather': weather}), 200


@stage_bp.route('/update-all-weather', methods=['POST'])
@login_required
@require_role('admin')
def update_all_weather():
    """Обновить погоду для ВСЕХ этапов сразу."""
    stages = Stage.get_all_with_weather()
    updated = 0
    for stage in stages:
        weather = Stage.update_weather(stage['id'])
        if weather:
            updated += 1
    return jsonify({
        'success': True,
        'updated': updated,
        'total': len(stages)
    }), 200


@stage_bp.route('/<int:stage_id>', methods=['PUT'])
@login_required
@require_role('marshal', 'admin')
def update_stage(stage_id):
    data = request.get_json()
    Stage.update(stage_id, **data)
    return jsonify({'success': True}), 200


@stage_bp.route('/<int:stage_id>', methods=['DELETE'])
@login_required
@require_role('admin')
def delete_stage(stage_id):
    Stage.delete(stage_id)
    return jsonify({'success': True}), 200