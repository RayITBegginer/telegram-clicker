from flask import Flask, request, jsonify, render_template
from database import Database, PETS, MAX_EQUIPPED_PETS
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()
app = Flask(__name__)
db = Database()

# Добавляем логирование
logging.basicConfig(level=logging.DEBUG)

# Упрощенная инициализация базы данных
if not os.path.exists('database.json'):
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump({}, f)

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if not user_id:
        return 'Требуется user_id'
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    stats = db.get_user_stats(user_id)
    stats['max_pets'] = MAX_EQUIPPED_PETS
    return jsonify(stats)

@app.route('/api/click', methods=['POST'])
def click():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    return jsonify(db.click(user_id))

@app.route('/api/upgrade_click', methods=['POST'])
def upgrade_click():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.upgrade_click(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/upgrade_passive', methods=['POST'])
def upgrade_passive():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.upgrade_passive(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/box', methods=['POST'])
def open_box():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.open_box(user_id)
    return jsonify(result if result else {'error': 'Недостаточно кликов'})

@app.route('/api/equip_pet', methods=['POST'])
def equip_pet():
    user_id = request.json.get('user_id')
    pet = request.json.get('pet')
    if not user_id or not pet:
        return jsonify({'error': 'Invalid request'}), 400
    result = db.equip_pet(user_id, pet)
    return jsonify(result if result else {'error': 'Не удалось экипировать питомца'})

@app.route('/api/unequip_pet', methods=['POST'])
def unequip_pet():
    user_id = request.json.get('user_id')
    pet = request.json.get('pet')
    if not user_id or not pet:
        return jsonify({'error': 'Invalid request'}), 400
    result = db.unequip_pet(user_id, pet)
    return jsonify(result if result else {'error': 'Не удалось снять питомца'})

@app.route('/api/passive_income', methods=['POST'])
def passive_income():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    result = db.passive_income(user_id)
    return jsonify(result if result else {'error': 'Нет пассивного дохода'})

@app.route('/api/pets')
def get_pets():
    return jsonify(PETS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 