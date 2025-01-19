from flask import Flask, render_template, request, jsonify
from database import Database, PETS
import os
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
db = Database()

# Добавляем логирование
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if not user_id:
        return 'Требуется user_id'
    return render_template('index.html')

@app.route('/api/click', methods=['POST'])
def click():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    return jsonify(db.click(user_id))

@app.route('/api/stats', methods=['GET'])
def get_stats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    return jsonify(db.get_user_stats(user_id))

@app.route('/api/box', methods=['POST'])
def open_box():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.open_box(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/save', methods=['POST'])
def save_progress():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    
    success = db.update_user(user_id, data)
    return jsonify({'success': success})

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    
    achievements = db.get_achievements(user_id)
    return jsonify(achievements)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    app.logger.debug('Получен запрос к таблице лидеров')
    try:
        limit = request.args.get('limit', default=50, type=int)
        leaderboard = db.get_leaderboard(limit)
        app.logger.debug(f'Получены данные: {leaderboard}')
        return jsonify(leaderboard)
    except Exception as e:
        app.logger.error(f'Ошибка при получении таблицы лидеров: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/upgrade_click', methods=['POST'])
def upgrade_click():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.upgrade_click(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/upgrade_passive', methods=['POST'])
def upgrade_passive():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.upgrade_passive(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/passive_income', methods=['POST'])
def passive_income():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.passive_income(user_id)
    return jsonify(result if result else {'error': 'Нет пассивного дохода'})

@app.route('/api/equip_pet', methods=['POST'])
def equip_pet():
    data = request.json
    user_id = data.get('user_id')
    pet = data.get('pet')
    if not user_id or not pet:
        return jsonify({'error': 'Invalid request'}), 400
    result = db.equip_pet(user_id, pet)
    return jsonify(result if result else {'error': 'Не удалось экипировать питомца'})

@app.route('/api/unequip_pet', methods=['POST'])
def unequip_pet():
    data = request.json
    user_id = data.get('user_id')
    pet = data.get('pet')
    if not user_id or not pet:
        return jsonify({'error': 'Invalid request'}), 400
    result = db.unequip_pet(user_id, pet)
    return jsonify(result if result else {'error': 'Не удалось снять питомца'})

@app.route('/api/pets')
def get_pets():
    return jsonify(PETS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 