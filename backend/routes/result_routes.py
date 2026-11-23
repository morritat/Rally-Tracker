"""Публичные маршруты результатов этапов."""
from flask import Blueprint, jsonify
from backend.database import Database
from backend.auth.decorators import login_required

result_bp = Blueprint('results', __name__, url_prefix='/api/results')


@result_bp.route('/stage/<int:stage_id>', methods=['GET'])
@login_required
def get_stage_results(stage_id):
    db = Database()
    rows = db.fetch_all(
        """SELECT r.id, r.stage_id, r.crew_id, r.time_seconds, r.penalty_seconds,
                  c.number, c.pilot_name, c.navigator_name, c.car_model
           FROM results r
           JOIN crews c ON c.id = r.crew_id
           WHERE r.stage_id = ?
           ORDER BY (r.time_seconds + r.penalty_seconds) ASC""",
        (stage_id,)
    )
    return jsonify({'success': True, 'results': rows}), 200
