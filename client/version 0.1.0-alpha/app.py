from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, session
import random
import json
import mimetypes
import os
from datetime import datetime

# Регистрируем MIME-тип для 3D-моделей .glb
mimetypes.add_type('model/gltf-binary', '.glb')

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Путь к файлу с пользователями
USERS_FILE = 'users.json'

# Дополнительная раздача public/
@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory('../public', filename)

@app.after_request
def no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Хранилище выбора устройства
device_choices = {}

# Загрузка пользователей из файла
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    # Проверка авторизации
    if 'username' in session:
        return render_template('vibor-ystroistva.html')
    return render_template('registration-wintozo.html')

@app.route('/registration')
def registration():
    return render_template('registration-wintozo.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    model = data.get('model', '')
    
    if not username or len(username) < 3:
        return jsonify({'error': 'Никнейм должен быть от 3 символов'}), 400
    
    if not password or len(password) < 4:
        return jsonify({'error': 'Пароль должен быть от 4 символов'}), 400
    
    if model not in ['bekon', 'cube']:
        return jsonify({'error': 'Выберите модель'}), 400
    
    users = load_users()
    
    if username in users:
        return jsonify({'error': 'Этот никнейм уже занят'}), 400
    
    users[username] = {
        'password': password,
        'model': model,
        'created_at': str(datetime.now())
    }
    
    save_users(users)
    
    # Сохраняем в сессии
    session['username'] = username
    session['model'] = model
    
    return jsonify({'success': True, 'username': username, 'model': model})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    users = load_users()
    
    if username not in users:
        return jsonify({'error': 'Пользователь не найден'}), 400
    
    if users[username]['password'] != password:
        return jsonify({'error': 'Неверный пароль'}), 400
    
    # Сохраняем в сессии
    session['username'] = username
    session['model'] = users[username]['model']
    
    return jsonify({'success': True, 'username': username, 'model': users[username]['model']})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    session.pop('model', None)
    return jsonify({'success': True})

@app.route('/api/user')
def api_user():
    if 'username' in session:
        users = load_users()
        username = session['username']
        if username in users:
            return jsonify({
                'username': username,
                'model': users[username]['model']
            })
    return jsonify({'error': 'Не авторизован'}), 401

@app.route('/api/select-device', methods=['POST'])
def select_device():
    data = request.json
    device = data.get('device', 'computer')
    return jsonify({'status': 'ok', 'device': device})

@app.route('/lobby/<device>')
def lobby(device):
    if device == 'mobile':
        return render_template('wintoblox-mobile-lobby-menu.html')
    return render_template('wintoblox-lobby.html')

@app.route('/game/<device>/<game_id>')
def game(device, game_id):
    return render_template(f'games/{game_id}.html', device=device)

@app.route('/api/games')
def api_games():
    games = [
        {'id': 'pobeg_vmesto_obby_wintoblox', 'name': 'Побег от Бр Бр Патапима', 'desc': 'Убегай от монстра!'},
        {'id': 'kalmara', 'name': 'Красный цвет, зеленый цвет', 'desc': '3D игра в кальмара'},
    ]
    return jsonify(games)

if __name__ == '__main__':
    app.secret_key = 'winto_blox_secret_key_alpha_2024'
    app.run(host='0.0.0.0', port=5000, debug=True)
