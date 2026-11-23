import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

app = Flask(__name__, static_folder=str(BASE_DIR / 'static'), static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key')

# API blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.stage_routes import stage_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.result_routes import result_bp

app.register_blueprint(auth_bp)
app.register_blueprint(stage_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(result_bp)

CLIENT_DIR = BASE_DIR / 'client'

@app.route('/')
def index():
    return send_from_directory(CLIENT_DIR, 'index.html')

@app.route('/<path:filename>')
def serve(filename):
    # Не отдаём произвольные файлы из проекта; клиентская папка — единственный источник.
    return send_from_directory(CLIENT_DIR, filename)

@app.route('/api/health')
def health():
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
            host='127.0.0.1', port=5000)
