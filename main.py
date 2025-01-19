import asyncio
import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from keyboards import get_webapp_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from database import Database

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
db = Database()

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

# Константы для питомцев
PETS = {
    'Котенок': {'name': 'Котенок', 'click_power': 1, 'rarity': 'Обычный'},
    'Щенок': {'name': 'Щенок', 'click_power': 1, 'rarity': 'Обычный'},
    'Хомяк': {'name': 'Хомяк', 'click_power': 2, 'rarity': 'Редкий'},
    'Попугай': {'name': 'Попугай', 'click_power': 2, 'rarity': 'Редкий'},
    'Единорог': {'name': 'Единорог', 'click_power': 3, 'rarity': 'Эпический'},
    'Дракон': {'name': 'Дракон', 'click_power': 5, 'rarity': 'Легендарный'}
}

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

def create_user(user_id):
    """Создает нового пользователя, если его нет в базе"""
    if str(user_id) not in db.users:
        db.users[str(user_id)] = {
            'clicks': 0,
            'click_power': 1,
            'passive_income': 0,
            'equipped_pets': [],
            'inventory': [],
            'achievements': {
                'clicks_made': 0,
                'boxes_opened': 0,
                'pets_collected': 0
            },
            'last_save': None
        }
        db.save()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
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
        "👋 Привет! Я бот-кликер.\n"
        "🎯 Кликай, улучшай, собирай питомцев!\n"
        "🏆 Соревнуйся с другими игроками!\n\n"
        "Нажми кнопку ниже, чтобы начать игру!",
        reply_markup=keyboard
    )

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 Помощь по игре:\n\n"
        "🖱 Кликай, чтобы получать очки\n"
        "💪 Улучшай силу клика\n"
        "⚡️ Увеличивай пассивный доход\n"
        "🎁 Открывай боксы с питомцами\n"
        "🐾 Питомцы увеличивают силу клика\n"
        "🏆 Соревнуйся в таблице лидеров\n\n"
        "Команды:\n"
        "/start - Начать игру\n"
        "/help - Показать эту справку\n"
        "/stats - Показать статистику"
    )
    await message.answer(help_text)

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
    user_id = message.from_user.id
    user = db.get_user_stats(user_id)
    
    if not user or not user.get('inventory'):
        await message.answer("У вас пока нет питомцев!")
        return
    
    pets_text = "Ваши питомцы:\n"
    for pet in user['inventory']:
        pet_info = pets[pet]
        pets_text += f"• {pet_info['name']} (Сила: +{pet_info['click_power']})\n"
    
    await message.answer(pets_text)

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
    if user_id in db.users:
        user = db.users[user_id]
        stats_text = (
            "📊 Ваша статистика:\n\n"
            f"💰 Клики: {user['clicks']}\n"
            f"💪 Сила клика: {user['click_power']}\n"
            f"⚡️ Пассивный доход: {user['passive_income']}/сек\n"
            f"🐾 Питомцев: {len(user['inventory'])}\n"
            f"👥 Экипировано: {len(user['equipped_pets'])}\n\n"
            f"🏆 Достижения:\n"
            f"👆 Всего кликов: {user['achievements']['clicks_made']}\n"
            f"📦 Боксов открыто: {user['achievements']['boxes_opened']}\n"
            f"🌟 Питомцев получено: {user['achievements']['pets_collected']}"
        )
        await message.answer(stats_text)
    else:
        await message.answer("❌ Вы еще не начали игру! Используйте /start")

@dp.message(Command('top'))
async def cmd_top(message: types.Message):
    leaderboard = db.get_leaderboard(limit=10)  # Получаем топ-10 игроков
    
    if not leaderboard:
        await message.answer("Пока никто не играл! Будьте первым! 🎮")
        return
    
    text = "🏆 Топ-10 игроков:\n\n"
    for i, player in enumerate(leaderboard, 1):
        # Добавляем эмодзи для первых трех мест
        medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '•')
        
        text += (
            f"{medal} {i}. ID: {player['user_id']}\n"
            f"   💰 Баланс: {player['clicks']}\n"
            f"   💪 Сила клика: {player['click_power']}\n"
            f"   🐾 Питомцев: {player['pets_count']}\n\n"
        )
    
    await message.answer(text)

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

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())