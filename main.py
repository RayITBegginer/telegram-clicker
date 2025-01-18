import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import *
from database import Database
from keyboards import get_main_keyboard, get_pets_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = db.get_user(user_id)
    await message.answer(
        'Добро пожаловать в игру! Кликайте, чтобы заработать монеты.',
        reply_markup=get_main_keyboard(user_data)
    )

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = db.get_user(user_id)
    
    if callback.data == 'click':
        user_data['clicks'] += user_data['click_power']
        if user_data['clicks'] % 5 == 0:
            db.update_user(user_id, user_data)
        await callback.message.edit_reply_markup(reply_markup=get_main_keyboard(user_data))
    
    elif callback.data == 'upgrade_click':
        upgrade_cost = int(BASE_CLICK_UPGRADE_COST * (CLICK_UPGRADE_COST_MULTIPLIER ** (user_data['base_click_power'] - 1)))
        if user_data['clicks'] >= upgrade_cost:
            user_data['clicks'] -= upgrade_cost
            user_data['base_click_power'] += 1
            db.recalculate_multipliers(user_id)
            user_data = db.get_user(user_id)
            await callback.answer(f'Улучшение куплено! Новая базовая сила клика: {user_data["base_click_power"]}')
        else:
            await callback.answer(f'Недостаточно монет! Нужно: {upgrade_cost}', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=get_main_keyboard(user_data))
    
    elif callback.data == 'upgrade_passive':
        upgrade_cost = int(BASE_PASSIVE_UPGRADE_COST * (PASSIVE_UPGRADE_COST_MULTIPLIER ** user_data['passive_income']))
        if user_data['clicks'] >= upgrade_cost:
            user_data['clicks'] -= upgrade_cost
            user_data['passive_income'] += 1
            db.recalculate_multipliers(user_id)
            user_data = db.get_user(user_id)
            await callback.answer(f'Пассивный доход улучшен! Новое значение: {user_data["passive_income"]}')
        else:
            await callback.answer(f'Недостаточно монет! Нужно: {upgrade_cost}', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=get_main_keyboard(user_data))
    
    elif callback.data == 'open_case':
        if user_data['clicks'] >= CASE_COST:
            user_data['clicks'] -= CASE_COST
            pet = get_random_pet()
            db.add_pet(user_id, pet)
            user_data = db.get_user(user_id)
            await callback.answer(f'Вы получили питомца: {pet.name}!', show_alert=True)
        else:
            await callback.answer(f'Недостаточно монет! Нужно: {CASE_COST}', show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=get_main_keyboard(user_data))
    
    elif callback.data == 'pets':
        equipped_count = len(user_data['equipped_pets'])
        text = f'🐾 Ваши питомцы (Экипировано: {equipped_count}/2)\n'
        text += f'Множитель клика: x{user_data["click_power"]/user_data["base_click_power"]:.1f}\n'
        text += f'Множитель пассива: x{user_data["passive_power"]/max(1, user_data["passive_income"]):.1f}'
        await callback.message.edit_text(text, reply_markup=get_pets_keyboard(user_data))
    
    elif callback.data.startswith('equip_'):
        pet_name = callback.data[6:]
        if db.equip_pet(user_id, pet_name):
            await callback.answer('Питомец экипирован!')
            user_data = db.get_user(user_id)
            equipped_count = len(user_data['equipped_pets'])
            text = f'🐾 Ваши питомцы (Экипировано: {equipped_count}/2)\n'
            text += f'Множитель клика: x{user_data["click_power"]/user_data["base_click_power"]:.1f}\n'
            text += f'Множитель пассива: x{user_data["passive_power"]/max(1, user_data["passive_income"]):.1f}'
            await callback.message.edit_text(text, reply_markup=get_pets_keyboard(user_data))
        else:
            await callback.answer('Нельзя экипировать больше 2 питомцев!', show_alert=True)
    
    elif callback.data.startswith('unequip_'):
        pet_name = callback.data[8:]
        if db.equip_pet(user_id, pet_name):
            await callback.answer('Питомец снят!')
            user_data = db.get_user(user_id)
            equipped_count = len(user_data['equipped_pets'])
            text = f'🐾 Ваши питомцы (Экипировано: {equipped_count}/2)\n'
            text += f'Множитель клика: x{user_data["click_power"]/user_data["base_click_power"]:.1f}\n'
            text += f'Множитель пассива: x{user_data["passive_power"]/max(1, user_data["passive_income"]):.1f}'
            await callback.message.edit_text(text, reply_markup=get_pets_keyboard(user_data))
    
    elif callback.data == 'back':
        await callback.message.edit_text('Главное меню:', reply_markup=get_main_keyboard(user_data))
    
    await callback.answer()

@dp.message(Command('play'))
async def cmd_play(message: types.Message):
    web_app_url = 'https://your-app-name.onrender.com'  # URL будет получен после деплоя
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="🎮 Играть", web_app=types.WebAppInfo(url=web_app_url))
    ]])
    await message.answer("Нажмите кнопку ниже, чтобы открыть игру:", reply_markup=keyboard)

async def passive_income():
    last_save = {}
    while True:
        try:
            current_time = asyncio.get_event_loop().time()
            for user_id, user_data in db.data.items():
                if user_data['passive_power'] > 0:
                    user_data['clicks'] += user_data['passive_power']
                    if user_id not in last_save or current_time - last_save[user_id] >= 5:
                        db.update_user(user_id, user_data)
                        last_save[user_id] = current_time
            await asyncio.sleep(PASSIVE_INCOME_INTERVAL)
        except Exception as e:
            logger.error(f"Ошибка в passive_income: {e}")
            await asyncio.sleep(1)

async def main():
    try:
        logger.info("Бот запущен")
        passive_income_task = asyncio.create_task(passive_income())
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        logger.info("Бот остановлен")
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот был остановлен вручную")