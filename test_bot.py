import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

TOKEN = '5908602592:AAGxNGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG'  # Ваш токен

async def main():
    bot = Bot(token=TOKEN)
    try:
        me = await bot.get_me()
        print(f"Бот успешно подключен: @{me.username}")
    except Exception as e:
        print(f"Ошибка при подключении: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 