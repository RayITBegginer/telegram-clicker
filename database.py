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
        """Инициализация базы данных"""
        self.filename = 'database.json'
        self.users = {}
        self.load()
        print("Database initialized")  # Отладка

    def load(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.users = data
                        print(f"Loaded data: {self.users}")  # Отладка
                    else:
                        print("Creating new database - invalid format")
                        self.users = {}
            else:
                print("Creating new database file")
                self.users = {}
                self.save()
        except Exception as e:
            print(f"Error loading database: {e}")
            self.users = {}

    def save(self):
        """Сохранение данных"""
        try:
            # Прямое сохранение в файл
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            print(f"Saved data: {self.users}")  # Отладка
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        user_id = str(user_id)
        if user_id not in self.users:
            print(f"Creating new user: {user_id}")  # Отладка
            self.users[user_id] = {
                'clicks': 0,
                'click_power': 1,
                'passive_income': 0,
                'inventory': [],
                'equipped_pets': [],
                'pet_counts': {}
            }
            self.save()
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
        """Обработка клика"""
        user = self.get_user_stats(user_id)
        user['clicks'] += user['click_power']
        self.save()  # Сохраняем после каждого клика
        return user

    def upgrade_click(self, user_id: str) -> Dict[str, Any]:
        """Улучшение силы клика с автоматическим обновлением множителей"""
        user = self.get_user_stats(user_id)
        cost = int(50 * (1.5 ** (user['click_power'] - 1)))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['click_power'] += 1
            
            # Автоматически обновляем множители
            click_mult, _ = self.calculate_multipliers(user)
            user['current_click_power'] = round(user['click_power'] * click_mult)
            
            self.save()
            return self.get_user_stats(user_id)
        return None

    def upgrade_passive(self, user_id: str) -> Dict[str, Any]:
        """Улучшение пассивного дохода с автоматическим обновлением множителей"""
        user = self.get_user_stats(user_id)
        cost = int(100 * (1.5 ** user['passive_income']))
        
        if user['clicks'] >= cost:
            user['clicks'] -= cost
            user['passive_income'] += 1
            
            # Автоматически обновляем множители
            _, passive_mult = self.calculate_multipliers(user)
            user['current_passive_income'] = round(user['passive_income'] * passive_mult)
            
            self.save()
            return self.get_user_stats(user_id)
        return None

    def open_box(self, user_id: str) -> Dict[str, Any]:
        """Открытие бокса с питомцем"""
        user = self.get_user_stats(user_id)
        if user['clicks'] >= 500:
            # Сначала снимаем клики
            user['clicks'] -= 500
            
            # Выбираем питомца
            pet = random.choice(list(PETS.keys()))
            
            # Добавляем в инвентарь
            if 'inventory' not in user:
                user['inventory'] = []
            user['inventory'].append(pet)
            
            # Сохраняем изменения
            success = self.save()
            
            if success:
                return {
                    'success': True,
                    'pet_info': PETS[pet],
                    'user_stats': self.get_user_stats(user_id)
                }
            else:
                # Возвращаем клики, если сохранение не удалось
                user['clicks'] += 500
                return None
        return None

    def equip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Экипировка питомца"""
        user = self.get_user_stats(user_id)
        
        # Проверяем количество в инвентаре и уже экипированных
        pet_count_in_inventory = user['inventory'].count(pet)
        pet_count_equipped = user['equipped_pets'].count(pet)
        
        # Можно экипировать, если есть в инвентаре и есть место
        if (pet in user['inventory'] and 
            len(user['equipped_pets']) < MAX_EQUIPPED_PETS and 
            pet_count_equipped < pet_count_in_inventory):
            
            user['equipped_pets'].append(pet)
            self.save()
            return self.get_user_stats(user_id)
        return None

    def equip_all_same(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Экипировка всех одинаковых питомцев"""
        user = self.get_user_stats(user_id)
        
        # Сколько можно экипировать
        available_slots = MAX_EQUIPPED_PETS - len(user['equipped_pets'])
        if available_slots <= 0:
            return None
            
        # Сколько неэкипированных питомцев этого типа
        total_count = user['inventory'].count(pet)
        equipped_count = user['equipped_pets'].count(pet)
        unequipped_count = total_count - equipped_count
        
        # Экипируем максимально возможное количество
        to_equip = min(available_slots, unequipped_count)
        
        if to_equip > 0:
            for _ in range(to_equip):
                user['equipped_pets'].append(pet)
            self.save()
            return self.get_user_stats(user_id)
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
            return self.get_user_stats(user_id)
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
            return self.get_user_stats(user_id)
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

    def unequip_pet(self, user_id: str, pet: str) -> Dict[str, Any]:
        """Снятие питомца"""
        user = self.get_user_stats(user_id)
        if pet in user['equipped_pets']:
            user['equipped_pets'].remove(pet)
            
            # Пересчитываем множители
            click_mult, passive_mult = self.calculate_multipliers(user)
            user['current_click_power'] = round(user['click_power'] * click_mult)
            user['current_passive_income'] = round(user['passive_income'] * passive_mult)
            
            self.save()
            return self.get_user_stats(user_id)
        return None 