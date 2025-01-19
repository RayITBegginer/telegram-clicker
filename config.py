import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

# Настройки игры
BOX_COST = 500
MAX_EQUIPPED_PETS = 2

# Питомцы и их характеристики
PETS = {
    'cat': {'name': 'Кот', 'click_power': 2, 'passive_income': 1, 'rarity': 'common'},
    'dog': {'name': 'Собака', 'click_power': 3, 'passive_income': 2, 'rarity': 'common'},
    'dragon': {'name': 'Дракон', 'click_power': 5, 'passive_income': 3, 'rarity': 'rare'},
    'unicorn': {'name': 'Единорог', 'click_power': 7, 'passive_income': 4, 'rarity': 'rare'},
    'phoenix': {'name': 'Феникс', 'click_power': 10, 'passive_income': 5, 'rarity': 'epic'}
}

# Шансы выпадения питомцев из боксов
BOX_CHANCES = {
    'common': 0.7,
    'rare': 0.25,
    'epic': 0.05
}

# Цвета для редкостей питомцев
RARITY_COLORS = {
    'common': '⚪️',
    'rare': '🔵',
    'epic': '🟣'
} 