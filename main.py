import asyncio
from os import getenv
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from Routes.Firstline import router
from db.db import init_db
#загрузка env файла / env file load
load_dotenv()
'''добавляем переменную для dispatcher(связывает код с тг),
 и переводим через router к файлу с командамы / adding variable for dispatcher, 
 and connect across router to command file'''
dp = Dispatcher()
dp.include_router(router)
#достаем в новую переменную с env файла токен / from env put the token in new variable
token= getenv('BOT_TOKEN')
#проверяем есть ли токен / check token accessibility
if not token:
    raise ValueError("doesn't have BOT_TOKEN")
#функция для подключения бота к проекту / function for connecting bot to project
async def Main():
#получения токена для бота / connect token to bot
    bot=Bot(token=token)
#для удобства вывод старта работы бота / for convenience, output while bot start
    print("Bot started")
#подключение базы данных / database connecting
    await init_db()
# попытка запуска бота / trying start bot
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

# запуск файла / starting file
if __name__ == '__main__':
    asyncio.run(Main())