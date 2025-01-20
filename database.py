import json
import os
from datetime import datetime
from config import PETS, BOX_CHANCES, BOX_COST
import random
from typing import Dict, Any

# Улучшенная система питомцев с уровнями
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
        """Инициализация базы данных с проверкой файла"""
        self.filename = 'database.json'
        if not os.path.exists(self.filename):
            self.users = {}
            self.save()
        else:
            self.load()

    def load(self):
        """Загрузка базы данных"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except:
            self.users = {}
            self.save()

    def save(self):
        """Безопасное сохранение базы данных"""
        try:
            # Создаем временный файл
            temp_file = f"{self.filename}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            # Безопасно заменяем основной файл
            os.replace(temp_file, self.filename)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Получение статистики пользователя с подсчетом питомцев"""
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {
                'clicks': 0,
                'click_power': 1,
                'passive_income': 0,
                'inventory': [],
                'equipped_pets': [],
                'pet_levels': {},  # Уровни питомцев
                'last_save': 0     # Timestamp последнего сохранения
            }
            self.save()
        
        # Подсчитываем количество каждого питомца
        pet_counts = {}
        for pet in self.users[user_id]['inventory']:
            pet_counts[pet] = pet_counts.get(pet, 0) + 1
        
        # Добавляем счетчики в статистику
        self.users[user_id]['pet_counts'] = pet_counts
        
        # Добавляем текущие множители в статистику
        click_mult, passive_mult = self.calculate_multipliers(self.users[user_id])
        self.users[user_id]['current_click_power'] = round(self.users[user_id]['click_power'] * click_mult)
        self.users[user_id]['current_passive_income'] = round(self.users[user_id]['passive_income'] * passive_mult)
        
        return self.users[user_id]

    def calculate_multipliers(self, user: Dict) -> tuple:
        """Расчет множителей от питомцев"""
        click_multiplier = 1.0
        passive_multiplier = 1.0
        
        # Учитываем все экипированные питомцы
        for pet in user['equipped_pets'][:MAX_EQUIPPED_PETS]:
            if pet in PETS:
                click_multiplier *= PETS[pet]['click_multiplier']
                passive_multiplier *= PETS[pet]['passive_multiplier']
        
        return click_multiplier, passive_multiplier

    def click(self, user_id: str) -> Dict[str, Any]:
        """Обработка клика с множителями"""
        user = self.get_user_stats(user_id)
        click_mult, _ = self.calculate_multipliers(user)
        
        # Применяем множитель к базовой силе клика
        total_power = int(user['click_power'] * click_mult)
        user['clicks'] += total_power
        
        # Сохраняем текущую силу клика для отображения
        user['current_click_power'] = total_power
        
        self.save()
        return user

    def upgrade_click(self, user_id: str) -> Dict[str, Any]:
        """Улучшение силы клика"""
        user = self.get_user_stats(user_id)
        cost = int(50 * (1.5 ** (user['click_power'] - 1)))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['click_power'] += 1
            self.save()
            return user
        return None

    def upgrade_passive(self, user_id: str) -> Dict[str, Any]:
        """Улучшение пассивного дохода"""
        user = self.get_user_stats(user_id)
        cost = int(100 * (1.5 ** user['passive_income']))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['passive_income'] += 1
            self.save()
            return user
        return None

    def open_box(self, user_id: str) -> Dict[str, Any]:
        """Открытие бокса с питомцем"""
        user = self.get_user_stats(user_id)
        if user['clicks'] >= 500:
            user['clicks'] -= 500
            pet = random.choice(list(PETS.keys()))
            user['inventory'].append(pet)
            self.save()
            return {
                'success': True,
                'pet_info': PETS[pet],
                'user_stats': user
            }
        return None

    def equip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Экипировка питомца с возможностью экипировать одинаковых"""
        user = self.get_user_stats(user_id)
        if pet in user['inventory']:
            # Проверяем, сколько таких питомцев уже экипировано
            equipped_count = user['equipped_pets'].count(pet)
            # Проверяем, сколько таких питомцев есть в инвентаре
            inventory_count = user['inventory'].count(pet)
            
            # Можно экипировать, если есть свободные питомцы этого типа
            if equipped_count < inventory_count:
                if len(user['equipped_pets']) < MAX_EQUIPPED_PETS:
                    user['equipped_pets'].append(pet)
                    
                    # Обновляем множители
                    click_mult, passive_mult = self.calculate_multipliers(user)
                    user['current_click_power'] = round(user['click_power'] * click_mult)
                    user['current_passive_income'] = round(user['passive_income'] * passive_mult)
                    
                    self.save()
                    return user
        return None

    def delete_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Удаление питомца из инвентаря"""
        user = self.get_user_stats(user_id)
        if pet in user['inventory']:
            # Если питомец экипирован, сначала снимаем его
            if pet in user['equipped_pets']:
                user['equipped_pets'].remove(pet)
            
            # Удаляем из инвентаря
            user['inventory'].remove(pet)
            
            # Обновляем множители
            click_mult, passive_mult = self.calculate_multipliers(user)
            user['current_click_power'] = round(user['click_power'] * click_mult)
            user['current_passive_income'] = round(user['passive_income'] * passive_mult)
            
            self.save()
            return user
        return None

    def passive_income(self, user_id: str) -> Dict[str, Any]:
        """Начисление пассивного дохода с множителями"""
        user = self.get_user_stats(user_id)
        _, passive_mult = self.calculate_multipliers(user)
        
        if user['passive_income'] > 0:
            # Применяем множитель к пассивному доходу
            income = round(user['passive_income'] * passive_mult)
            user['clicks'] += income
            
            # Обновляем текущие значения
            click_mult, _ = self.calculate_multipliers(user)
            user['current_click_power'] = round(user['click_power'] * click_mult)
            user['current_passive_income'] = income
            
            self.save()
            return user
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
                'pet_levels': {},
                'last_save': datetime.now().isoformat()
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

    def upgrade_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Улучшение питомца"""
        user = self.get_user_stats(user_id)
        if pet not in user['inventory']:
            return None
            
        current_level = user['pet_levels'].get(pet, 1)
        if current_level >= PETS[pet]['max_level']:
            return {'error': 'Достигнут максимальный уровень'}
            
        upgrade_cost = PETS[pet]['upgrade_cost'] * current_level
        if user['clicks'] < upgrade_cost:
            return {'error': 'Недостаточно кликов'}
            
        user['clicks'] -= upgrade_cost
        user['pet_levels'][pet] = current_level + 1
        self.save()
        
        return {
            'success': True,
            'new_level': current_level + 1,
            'user_stats': user
        } 