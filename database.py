import json
import os
from typing import Dict, Any
from config import Pet

class Database:
    def __init__(self, filename: str = 'users.json'):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def _save_data(self) -> None:
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)

    def get_user(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.data:
            self.data[user_id] = {
                "clicks": 0,
                "base_click_power": 1,
                "passive_income": 0,
                "pets_inventory": {},
                "equipped_pets": [],
                "click_power": 1,
                "passive_power": 0
            }
            self._save_data()
        return self.data[user_id]

    def update_user(self, user_id: str, data: Dict[str, Any]) -> None:
        self.data[user_id] = data
        self._save_data()

    def add_pet(self, user_id: str, pet: Pet) -> None:
        user = self.get_user(user_id)
        pet_key = f"{pet.name}"
        
        if pet_key in user['pets_inventory']:
            user['pets_inventory'][pet_key]['count'] += 1
        else:
            user['pets_inventory'][pet_key] = {
                'count': 1,
                'data': {
                    "name": pet.name,
                    "emoji": pet.emoji,
                    "click_mult": pet.click_multiplier,
                    "passive_mult": pet.passive_multiplier
                }
            }
        
        self.update_user(user_id, user)

    def equip_pet(self, user_id: str, pet_name: str) -> bool:
        user = self.get_user(user_id)
        
        if pet_name not in user['pets_inventory'] or user['pets_inventory'][pet_name]['count'] < 1:
            return False
        
        if any(pet['name'] == pet_name for pet in user['equipped_pets']):
            user['equipped_pets'] = [pet for pet in user['equipped_pets'] if pet['name'] != pet_name]
        else:
            if len(user['equipped_pets']) >= 2:
                return False
            user['equipped_pets'].append(user['pets_inventory'][pet_name]['data'])
        
        self.recalculate_multipliers(user_id)
        return True

    def recalculate_multipliers(self, user_id: str) -> None:
        user = self.get_user(user_id)
        
        total_click_mult = 0
        total_passive_mult = 0
        
        for pet in user['equipped_pets']:
            total_click_mult += pet['click_mult'] - 1
            total_passive_mult += pet['passive_mult'] - 1
        
        user['click_power'] = user['base_click_power'] * (1 + total_click_mult)
        user['passive_power'] = user['passive_income'] * (1 + total_passive_mult)
        
        self.update_user(user_id, user) 