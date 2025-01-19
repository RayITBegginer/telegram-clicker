from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from config import WEBAPP_URL

def get_webapp_keyboard():
    """Создает клавиатуру с кнопкой для открытия веб-приложения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Играть",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    return keyboard

def get_inventory_keyboard(inventory, equipped_pets):
    """Создает клавиатуру для инвентаря питомцев"""
    keyboard = []
    for i, pet_type in enumerate(set(inventory), 1):
        count = inventory.count(pet_type)
        status = "🟢" if pet_type in equipped_pets else "⚪"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {i}. {pets[pet_type]['name']} (x{count})",
                callback_data=f"equip_{i-1}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 