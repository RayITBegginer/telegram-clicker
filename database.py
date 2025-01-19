import json
import os
from datetime import datetime
from config import PETS, BOX_CHANCES, BOX_COST
import random
from typing import Dict, Any

class Database:
    def __init__(self, filename: str = 'database.json'):
        self.filename = filename
        try:
            with open(filename, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
        
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=2)

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                'clicks': 0,
                'click_power': 1,
                'passive_income': 0,
                'inventory': [],
                'equipped_pets': [],
                'achievements': {
                    'clicks_made': 0,
                    'boxes_opened': 0,
                    'pets_collected': 0
                }
            }
            self.save()
        return self.users[str(user_id)]

    def click(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        
        # Подсчет силы клика с учетом питомцев
        click_power = user['click_power']
        for pet in user['equipped_pets']:
            if pet in PETS:
                click_power += PETS[pet]['click_power']
        
        user['clicks'] += click_power
        user['achievements']['clicks_made'] += 1
        self.save()
        return user

    def upgrade_click(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        cost = int(50 * (1.5 ** (user['click_power'] - 1)))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['click_power'] += 1
            self.save()
            return user
        return None

    def upgrade_passive(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        cost = int(100 * (1.5 ** user['passive_income']))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['passive_income'] += 1
            self.save()
            return user
        return None

    def open_box(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if user['clicks'] >= 500:
            user['clicks'] -= 500
            pet = random.choice(list(PETS.keys()))
            user['inventory'].append(pet)
            user['achievements']['boxes_opened'] += 1
            user['achievements']['pets_collected'] += 1
            self.save()
            return {
                'pet_info': PETS[pet],
                'user_stats': user
            }
        return None

    def equip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if pet in user['inventory'] and pet not in user['equipped_pets']:
            user['equipped_pets'].append(pet)
            self.save()
        return user

    def unequip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if pet in user['equipped_pets']:
            user['equipped_pets'].remove(pet)
            self.save()
        return user

    def passive_income(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if user['passive_income'] > 0:
            user['clicks'] += user['passive_income']
            self.save()
        return user

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