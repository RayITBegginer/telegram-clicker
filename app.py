from flask import Flask, render_template, request, jsonify
from database import Database
from config import *

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        user_id = str(data['user_id'])
        action = data['action']
        user_data = db.get_user(user_id)
        
        if action == 'get_data':
            return jsonify({'success': True, 'data': user_data})
        
        if action == 'click':
            user_data['clicks'] += user_data['click_power']
        
        elif action == 'upgrade_click':
            upgrade_cost = int(BASE_CLICK_UPGRADE_COST * (CLICK_UPGRADE_COST_MULTIPLIER ** (user_data['base_click_power'] - 1)))
            if user_data['clicks'] >= upgrade_cost:
                user_data['clicks'] -= upgrade_cost
                user_data['base_click_power'] += 1
                db.recalculate_multipliers(user_id)
        
        elif action == 'upgrade_passive':
            upgrade_cost = int(BASE_PASSIVE_UPGRADE_COST * (PASSIVE_UPGRADE_COST_MULTIPLIER ** user_data['passive_income']))
            if user_data['clicks'] >= upgrade_cost:
                user_data['clicks'] -= upgrade_cost
                user_data['passive_income'] += 1
                db.recalculate_multipliers(user_id)
        
        elif action == 'open_case':
            if user_data['clicks'] >= CASE_COST:
                user_data['clicks'] -= CASE_COST
                pet = get_random_pet()
                db.add_pet(user_id, pet)
        
        elif action in ['equip_pet', 'unequip_pet']:
            db.equip_pet(user_id, data['pet_name'])
        
        db.update_user(user_id, user_data)
        return jsonify({'success': True, 'data': db.get_user(user_id)})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 