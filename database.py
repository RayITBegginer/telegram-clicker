import json
import random
from config import PETS, BOX_CHANCES, BOX_COST

class Database:
    def __init__(self):
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
            self.save()

    def save(self):
        with open('users.json', 'w') as f:
            json.dump(self.users, f)

    def create_user(self, user_id):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                'clicks': 0,
                'click_power': 1,
                'passive_income': 0,
                'inventory': [],
                'equipped_pets': []
            }
            self.save()
        return self.users[str(user_id)]

    def get_user_stats(self, user_id):
        user = self.users.get(str(user_id))
        if not user:
            user = self.create_user(user_id)
        
        # Подсчет общей силы клика и пассивного дохода
        total_click_power = user['click_power']
        total_passive_income = user['passive_income']
        
        for pet_type in user['equipped_pets']:
            total_click_power += PETS[pet_type]['click_power']
            total_passive_income += PETS[pet_type]['passive_income']
        
        return {
            'clicks': user['clicks'],
            'click_power': total_click_power,
            'passive_income': total_passive_income,
            'inventory': user['inventory'],
            'equipped_pets': user['equipped_pets']
        }

    def click(self, user_id):
        user = self.users.get(str(user_id))
        if not user:
            user = self.create_user(user_id)
        
        # Подсчет силы клика с учетом питомцев
        click_power = user['click_power']
        for pet_type in user['equipped_pets']:
            click_power += PETS[pet_type]['click_power']
        
        user['clicks'] += click_power
        self.save()
        
        return self.get_user_stats(user_id)

    def buy_box(self, user_id):
        user = self.users.get(str(user_id))
        if not user:
            return None
        
        if user['clicks'] < BOX_COST:
            return None
        
        user['clicks'] -= BOX_COST
        
        # Определяем редкость питомца
        rarity = random.choices(
            list(BOX_CHANCES.keys()),
            list(BOX_CHANCES.values())
        )[0]
        
        # Выбираем случайного питомца этой редкости
        possible_pets = [pet_type for pet_type, pet in PETS.items() if pet['rarity'] == rarity]
        pet_type = random.choice(possible_pets)
        
        # Добавляем питомца в инвентарь
        user['inventory'].append(pet_type)
        self.save()
        
        return {
            'pet_type': pet_type,
            'pet_info': PETS[pet_type],
            'user_stats': self.get_user_stats(user_id)
        }

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