import json
import os
from datetime import datetime
from config import PETS, BOX_CHANCES, BOX_COST

class Database:
    def __init__(self):
        self.filename = 'users.json'
        self.load_data()
        
    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                formatted_data = json.load(f)
                # Преобразуем обратно в рабочий формат
                self.users = {}
                for user_id, formatted_user in formatted_data.items():
                    self.users[user_id] = {
                        'clicks': formatted_user['Основная информация']['Всего кликов'],
                        'click_power': formatted_user['Основная информация']['Сила клика'],
                        'passive_income': formatted_user['Основная информация']['Пассивный доход'],
                        'last_save': formatted_user['Основная информация']['Последнее сохранение'],
                        'equipped_pets': [pet_type for pet_type, pet_info in PETS.items() 
                                       if pet_info['name'] in formatted_user['Питомцы']['Экипировано']],
                        'inventory': [pet_type for pet_type, pet_info in PETS.items() 
                                    if pet_info['name'] in formatted_user['Питомцы']['В инвентаре']],
                        'achievements': {
                            'clicks_made': formatted_user['Достижения']['Всего кликов сделано'],
                            'boxes_opened': formatted_user['Достижения']['Боксов открыто'],
                            'pets_collected': formatted_user['Достижения']['Питомцев получено']
                        }
                    }
        except FileNotFoundError:
            self.users = {}

    def save(self):
        # Создаем бэкап перед сохранением
        if os.path.exists(self.filename):
            backup_name = f'users_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            os.rename(self.filename, backup_name)
        
        # Форматируем данные для сохранения
        formatted_data = {}
        for user_id, user_data in self.users.items():
            formatted_data[user_id] = {
                "Основная информация": {
                    "Всего кликов": user_data['clicks'],
                    "Сила клика": user_data['click_power'],
                    "Пассивный доход": user_data['passive_income'],
                    "Последнее сохранение": user_data['last_save']
                },
                "Питомцы": {
                    "Экипировано": [PETS[pet]['name'] for pet in user_data['equipped_pets']],
                    "В инвентаре": [PETS[pet]['name'] for pet in user_data['inventory']]
                },
                "Достижения": {
                    "Всего кликов сделано": user_data['achievements']['clicks_made'],
                    "Боксов открыто": user_data['achievements']['boxes_opened'],
                    "Питомцев получено": user_data['achievements']['pets_collected']
                }
            }
        
        # Сохраняем отформатированные данные
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)

    def create_user(self, user_id):
        str_id = str(user_id)
        if str_id not in self.users:
            self.users[str_id] = {
                'clicks': 0,
                'click_power': 1,
                'passive_income': 0,
                'inventory': [],
                'equipped_pets': [],
                'last_save': datetime.now().isoformat(),
                'achievements': {
                    'clicks_made': 0,
                    'boxes_opened': 0,
                    'pets_collected': 0
                }
            }
            self.save()
        return self.users[str_id]

    def update_user(self, user_id, data):
        str_id = str(user_id)
        if str_id in self.users:
            self.users[str_id].update(data)
            self.users[str_id]['last_save'] = datetime.now().isoformat()
            self.save()
            return True
        return False

    def get_user_stats(self, user_id):
        str_id = str(user_id)
        if str_id not in self.users:
            return self.create_user(user_id)
        return self.users[str_id]

    def click(self, user_id):
        user = self.get_user_stats(user_id)
        
        # Подсчет силы клика с учетом питомцев
        click_power = user['click_power']
        for pet_type in user['equipped_pets']:
            click_power += PETS[pet_type]['click_power']
        
        user['clicks'] += click_power
        user['achievements']['clicks_made'] += 1
        self.save()
        
        return user

    def buy_box(self, user_id):
        user = self.get_user_stats(user_id)
        
        if user['clicks'] < BOX_COST:
            return None
            
        user['clicks'] -= BOX_COST
        user['achievements']['boxes_opened'] += 1
        
        # Логика получения питомца из бокса
        pet = self.get_random_pet()
        user['inventory'].append(pet)
        user['achievements']['pets_collected'] += 1
        
        self.save()
        return {
            'user_stats': user,
            'pet_info': PETS[pet]
        }

    def get_achievements(self, user_id):
        user = self.get_user_stats(user_id)
        return user.get('achievements', {})

    def get_backup_list(self):
        """Получить список всех бэкапов"""
        backups = []
        for file in os.listdir():
            if file.startswith('users_backup_') and file.endswith('.json'):
                backups.append(file)
        return sorted(backups, reverse=True)

    def restore_from_backup(self, backup_name):
        """Восстановить данные из бэкапа"""
        try:
            with open(backup_name, 'r') as f:
                self.users = json.load(f)
            self.save()
            return True
        except:
            return False

    def equip_pet(self, user_id, pet_index):
        user = self.users.get(str(user_id))
        if not user:
            return False
        
        try:
            available_pets = list(set(user['inventory']))
            pet_type = available_pets[pet_index]
        except:
            return False
        
        if len(user['equipped_pets']) >= 2:
            return False
        
        if pet_type in user['equipped_pets']:
            return False
        
        user['equipped_pets'].append(pet_type)
        self.save()
        return True

    def unequip_pet(self, user_id, pet_index):
        user = self.users.get(str(user_id))
        if not user:
            return False
        
        try:
            pet_type = user['equipped_pets'][pet_index]
        except:
            return False
        
        user['equipped_pets'].remove(pet_type)
        self.save()
        return True

    def get_leaderboard(self, limit=50):
        """Получаем топ игроков по кликам"""
        players = []
        for user_id, data in self.users.items():
            players.append({
                'user_id': user_id,
                'clicks': data['clicks'],
                'pets_count': len(data['equipped_pets']),
                'click_power': data['click_power']
            })
        
        # Сортируем по количеству кликов
        sorted_players = sorted(players, key=lambda x: x['clicks'], reverse=True)
        
        return sorted_players[:limit] 