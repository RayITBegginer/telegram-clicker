import json
import os
from datetime import datetime
from config import PETS, BOX_CHANCES, BOX_COST
import random
from typing import Dict, Any

PETS = {
    'Котенок': {'name': 'Котенок', 'click_multiplier': 1.2, 'passive_multiplier': 1.1, 'rarity': 'Обычный'},
    'Щенок': {'name': 'Щенок', 'click_multiplier': 1.2, 'passive_multiplier': 1.2, 'rarity': 'Обычный'},
    'Хомяк': {'name': 'Хомяк', 'click_multiplier': 1.5, 'passive_multiplier': 1.3, 'rarity': 'Редкий'},
    'Попугай': {'name': 'Попугай', 'click_multiplier': 1.5, 'passive_multiplier': 1.5, 'rarity': 'Редкий'},
    'Единорог': {'name': 'Единорог', 'click_multiplier': 2.0, 'passive_multiplier': 1.8, 'rarity': 'Эпический'},
    'Дракон': {'name': 'Дракон', 'click_multiplier': 3.0, 'passive_multiplier': 2.0, 'rarity': 'Легендарный'}
}

MAX_EQUIPPED_PETS = 2

class Database:
    def __init__(self):
        try:
            with open('database.json', 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
            self.save()

    def save(self):
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

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

    def calculate_multipliers(self, user: Dict) -> tuple:
        click_multiplier = 1.0
        passive_multiplier = 1.0
        
        for pet in user['equipped_pets'][:MAX_EQUIPPED_PETS]:
            if pet in PETS:
                click_multiplier *= PETS[pet]['click_multiplier']
                passive_multiplier *= PETS[pet]['passive_multiplier']
        
        return click_multiplier, passive_multiplier

    def click(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        click_mult, _ = self.calculate_multipliers(user)
        
        total_power = int(user['click_power'] * click_mult)
        user['clicks'] += total_power
        user['achievements']['clicks_made'] += 1
        self.save()
        
        return {
            'clicks': user['clicks'],
            'click_power': total_power,
            'passive_income': user['passive_income'],
            'inventory': user['inventory'],
            'equipped_pets': user['equipped_pets']
        }

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
            
            total_click, total_passive = self.calculate_multipliers(user)
            
            return {
                'success': True,
                'pet_info': {
                    'name': pet,
                    'click_power': PETS[pet]['click_power'],
                    'passive_power': PETS[pet]['passive_multiplier'],
                    'rarity': PETS[pet]['rarity']
                },
                'user_stats': {
                    'clicks': user['clicks'],
                    'click_power': int(user['click_power'] * total_click),
                    'passive_income': int(user['passive_income'] * total_passive),
                    'inventory': user['inventory'],
                    'equipped_pets': user['equipped_pets']
                }
            }
        return {'success': False, 'error': 'Недостаточно кликов'}

    def equip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if pet in user['inventory'] and pet not in user['equipped_pets']:
            if len(user['equipped_pets']) < MAX_EQUIPPED_PETS:
                user['equipped_pets'].append(pet)
                self.save()
                
                total_click, total_passive = self.calculate_multipliers(user)
                
                return {
                    'clicks': user['clicks'],
                    'click_power': int(user['click_power'] * total_click),
                    'passive_income': int(user['passive_income'] * total_passive),
                    'inventory': user['inventory'],
                    'equipped_pets': user['equipped_pets'],
                    'max_pets': MAX_EQUIPPED_PETS
                }
        return None

    def unequip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        if pet in user['equipped_pets']:
            user['equipped_pets'].remove(pet)
            self.save()
            
            total_click, total_passive = self.calculate_multipliers(user)
            
            return {
                'clicks': user['clicks'],
                'click_power': int(user['click_power'] * total_click),
                'passive_income': int(user['passive_income'] * total_passive),
                'inventory': user['inventory'],
                'equipped_pets': user['equipped_pets']
            }
        return None

    def passive_income(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user_stats(user_id)
        _, passive_mult = self.calculate_multipliers(user)
        
        if user['passive_income'] > 0:
            total_passive = int(user['passive_income'] * passive_mult)
            user['clicks'] += total_passive
            self.save()
            
            total_click, _ = self.calculate_multipliers(user)
            
            return {
                'clicks': user['clicks'],
                'click_power': int(user['click_power'] * total_click),
                'passive_income': total_passive,
                'inventory': user['inventory'],
                'equipped_pets': user['equipped_pets']
            }
        return None

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