from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

def get_main_keyboard(user_data: dict) -> InlineKeyboardMarkup:
    click_upgrade_cost = int(BASE_CLICK_UPGRADE_COST * (CLICK_UPGRADE_COST_MULTIPLIER ** (user_data['base_click_power'] - 1)))
    passive_upgrade_cost = int(BASE_PASSIVE_UPGRADE_COST * (PASSIVE_UPGRADE_COST_MULTIPLIER ** user_data['passive_income']))
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f'💰 Баланс: {int(user_data["clicks"])}', callback_data='balance'),
            InlineKeyboardButton(text='🖱 Клик!', callback_data='click')
        ],
        [
            InlineKeyboardButton(
                text=f'⚡️ Сила клика: {user_data["click_power"]:.1f}',
                callback_data='show_click_power'
            )
        ],
        [
            InlineKeyboardButton(
                text=f'⏰ Пассивный доход: {user_data["passive_power"]:.1f}/сек',
                callback_data='show_passive_power'
            )
        ],
        [
            InlineKeyboardButton(text=f'🔄 Улучшить клик ({click_upgrade_cost})', callback_data='upgrade_click'),
            InlineKeyboardButton(text=f'🔄 Улучшить пассив ({passive_upgrade_cost})', callback_data='upgrade_passive')
        ],
        [
            InlineKeyboardButton(text=f'📦 Открыть кейс ({CASE_COST})', callback_data='open_case'),
            InlineKeyboardButton(text='🐾 Питомцы', callback_data='pets')
        ]
    ])

def get_pets_keyboard(user_data: dict) -> InlineKeyboardMarkup:
    keyboard = []
    
    # Показываем экипированных питомцев
    equipped = user_data['equipped_pets']
    if equipped:
        keyboard.append([InlineKeyboardButton(text="🎮 Экипированные питомцы:", callback_data="none")])
        for pet in equipped:
            keyboard.append([
                InlineKeyboardButton(
                    text=f'{pet["emoji"]} {pet["name"]} (x{pet["click_mult"]:.1f} клик, x{pet["passive_mult"]:.1f} пассив)',
                    callback_data=f'unequip_{pet["name"]}'
                )
            ])
    
    # Показываем инвентарь
    keyboard.append([InlineKeyboardButton(text="📦 Инвентарь:", callback_data="none")])
    for pet_name, pet_data in user_data['pets_inventory'].items():
        keyboard.append([
            InlineKeyboardButton(
                text=f'{pet_data["data"]["emoji"]} {pet_name} x{pet_data["count"]} '
                     f'(x{pet_data["data"]["click_mult"]:.1f} клик, x{pet_data["data"]["passive_mult"]:.1f} пассив)',
                callback_data=f'equip_{pet_name}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text='◀️ Назад', callback_data='back')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 