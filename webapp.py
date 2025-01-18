from flask import Flask, render_template, request, jsonify
from database import Database
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
db = Database()

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

if __name__ == '__main__':
    app.run(debug=True) 