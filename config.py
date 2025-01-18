import random
from dataclasses import dataclass
from typing import List

# Конфигурация бота
TOKEN = '7512002879:AAETdulKoJHOolQSDLxiyxPT6oCDea2cFsQ'  # Ваш токен

# Настройки игры
PASSIVE_INCOME_INTERVAL = 1  # Изменили на 1 секунду
CLICK_UPGRADE_COST_MULTIPLIER = 1.5  # Множитель стоимости улучшений клика
PASSIVE_UPGRADE_COST_MULTIPLIER = 2.0  # Множитель стоимости пассивного дохода
BASE_CLICK_UPGRADE_COST = 10  # Базовая стоимость улучшения клика
BASE_PASSIVE_UPGRADE_COST = 50  # Базовая стоимость пассивного дохода
CASE_COST = 150  # Стоимость кейса

@dataclass
class Pet:
    name: str
    emoji: str
    click_multiplier: float
    passive_multiplier: float
    chance: float  # Шанс выпадения в процентах

# Список доступных питомцев
PETS = [
    Pet("Обычная Кошка", "🐱", 1.5, 1.2, 40),
    Pet("Редкая Собака", "🐕", 2.0, 1.5, 30),
    Pet("Эпический Дракон", "🐲", 2.5, 2.0, 15),
    Pet("Легендарная Феникс", "🦅", 3.0, 2.5, 10),
    Pet("Мифический Единорог", "🦄", 4.0, 3.0, 5),
]

def get_random_pet() -> Pet:
    return random.choices(PETS, weights=[pet.chance for pet in PETS], k=1)[0] 