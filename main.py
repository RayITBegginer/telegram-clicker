import asyncio
import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from keyboards import get_webapp_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Загрузка данных пользователей
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

# Питомцы и их характеристики
pets = {
    'cat': {'name': 'Кот', 'click_power': 2, 'passive_income': 1, 'rarity': 'common'},
    'dog': {'name': 'Собака', 'click_power': 3, 'passive_income': 2, 'rarity': 'common'},
    'dragon': {'name': 'Дракон', 'click_power': 5, 'passive_income': 3, 'rarity': 'rare'},
    'unicorn': {'name': 'Единорог', 'click_power': 7, 'passive_income': 4, 'rarity': 'rare'},
    'phoenix': {'name': 'Феникс', 'click_power': 10, 'passive_income': 5, 'rarity': 'epic'}
}

# Шансы выпадения питомцев из боксов
box_chances = {
    'common': 0.7,
    'rare': 0.25,
    'epic': 0.05
}

BOX_COST = 500

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

def create_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            'clicks': 0,
            'click_power': 1,
            'passive_income': 0,
            'inventory': [],
            'equipped_pets': []
        }
        save_users()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    create_user(user_id)
    
    # Добавляем user_id в URL
    webapp_url = f"{os.getenv('WEBAPP_URL')}?user_id={user_id}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Играть",
            web_app=WebAppInfo(url=webapp_url)
        )]
    ])
    
    await message.answer(
        "Привет! Я бот-кликер.\n"
        "Нажми на кнопку ниже, чтобы начать игру!",
        reply_markup=keyboard
    )

@dp.message(Command('click'))
async def cmd_click(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    # Подсчет силы клика с учетом питомцев
    click_power = users[user_id]['click_power']
    for pet_type in users[user_id]['equipped_pets']:
        click_power += pets[pet_type]['click_power']
    
    users[user_id]['clicks'] += click_power
    save_users()
    
    await message.answer(f"Клик! +{click_power}\nВсего: {users[user_id]['clicks']} кликов")

@dp.message(Command('box'))
async def cmd_box(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    if users[user_id]['clicks'] < BOX_COST:
        await message.answer(f"Недостаточно кликов! Нужно {BOX_COST}")
        return
    
    users[user_id]['clicks'] -= BOX_COST
    
    # Определяем редкость питомца
    rarity = random.choices(
        list(box_chances.keys()),
        list(box_chances.values())
    )[0]
    
    # Выбираем случайного питомца этой редкости
    possible_pets = [pet_type for pet_type, pet in pets.items() if pet['rarity'] == rarity]
    pet_type = random.choice(possible_pets)
    
    # Добавляем питомца в инвентарь
    users[user_id]['inventory'].append(pet_type)
    save_users()
    
    await message.answer(
        f"🎉 Вы получили питомца: {pets[pet_type]['name']}!\n"
        f"Редкость: {rarity}\n"
        f"Клик: +{pets[pet_type]['click_power']}\n"
        f"Пассив: +{pets[pet_type]['passive_income']}"
    )

@dp.message(Command('inventory'))
async def cmd_inventory(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    if not users[user_id]['inventory']:
        await message.answer("У вас нет питомцев! Используйте /box чтобы получить питомца.")
        return
    
    # Считаем количество каждого питомца
    pet_counts = {}
    for pet_type in users[user_id]['inventory']:
        pet_counts[pet_type] = pet_counts.get(pet_type, 0) + 1
    
    # Формируем список питомцев
    inventory_list = []
    for i, (pet_type, count) in enumerate(pet_counts.items(), 1):
        status = "🟢" if pet_type in users[user_id]['equipped_pets'] else "⚪"
        inventory_list.append(
            f"{status} {i}. {pets[pet_type]['name']} (x{count})\n"
            f"└ Клик: +{pets[pet_type]['click_power']}, "
            f"Пассив: +{pets[pet_type]['passive_income']}"
        )
    
    await message.answer(
        f"Ваши питомцы:\n\n"
        f"{chr(10).join(inventory_list)}\n\n"
        f"Команды:\n"
        f"/equip [номер] - экипировать питомца\n"
        f"/unequip [номер] - снять питомца"
    )

@dp.message(Command('equip'))
async def cmd_equip(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    try:
        pet_index = int(message.text.split()[1]) - 1
        available_pets = list(set(users[user_id]['inventory']))
        pet_type = available_pets[pet_index]
    except:
        await message.answer("Используйте: /equip [номер питомца из инвентаря]")
        return
    
    if len(users[user_id]['equipped_pets']) >= 2:
        await message.answer("Уже экипировано максимальное количество питомцев (2)!")
        return
    
    if pet_type in users[user_id]['equipped_pets']:
        await message.answer(f"{pets[pet_type]['name']} уже экипирован!")
        return
    
    users[user_id]['equipped_pets'].append(pet_type)
    save_users()
    
    await message.answer(f"Вы экипировали {pets[pet_type]['name']}!")

@dp.message(Command('unequip'))
async def cmd_unequip(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    try:
        pet_index = int(message.text.split()[1]) - 1
        pet_type = users[user_id]['equipped_pets'][pet_index]
    except:
        await message.answer("Используйте: /unequip [номер экипированного питомца]")
        return
    
    users[user_id]['equipped_pets'].remove(pet_type)
    save_users()
    
    await message.answer(f"Вы сняли {pets[pet_type]['name']}!")

@dp.message(Command('stats'))
async def cmd_stats(message: types.Message):
    user_id = str(message.from_user.id)
    create_user(user_id)
    
    stats = users[user_id]
    
    # Подсчет общей силы клика и пассивного дохода
    total_click_power = stats['click_power']
    total_passive_income = stats['passive_income']
    
    for pet_type in stats['equipped_pets']:
        total_click_power += pets[pet_type]['click_power']
        total_passive_income += pets[pet_type]['passive_income']
    
    # Формируем список питомцев
    pets_list = "\n".join([f"- {pets[pet]['name']}" for pet in stats['equipped_pets']]) if stats['equipped_pets'] else "Нет питомцев"
    
    await message.answer(
        f"Ваша статистика:\n"
        f"Клики: {stats['clicks']}\n"
        f"Общая сила клика: {total_click_power}\n"
        f"Общий пассивный доход: {total_passive_income}/сек\n"
        f"\nЭкипированные питомцы:\n{pets_list}"
    )

# Пассивный доход
async def passive_income():
    while True:
        for user_id in users:
            passive = users[user_id]['passive_income']
            for pet_type in users[user_id]['equipped_pets']:
                passive += pets[pet_type]['passive_income']
            users[user_id]['clicks'] += passive
        save_users()
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))