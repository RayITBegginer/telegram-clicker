from flask import Flask, render_template, request, jsonify
from database import Database
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
    return render_template('index.html')

@app.route('/api/click', methods=['POST'])
def click():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    
    # Обновляем клики пользователя
    user_stats = db.click(user_id)
    return jsonify(user_stats)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    
    # Получаем статистику пользователя
    stats = db.get_user_stats(user_id)
    return jsonify(stats)

@app.route('/api/box', methods=['POST'])
def open_box():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'No user_id provided'}), 400
    
    # Открываем бокс
    result = db.buy_box(user_id)
    if not result:
        return jsonify({'error': 'Not enough clicks'}), 400
    
    return jsonify(result)

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

if __name__ == '__main__':
    app.run(debug=True) 