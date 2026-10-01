from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from aiogram import Dispatcher, Bot
from aiogram.types import Update
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
#секретный ключ для защиты webhook / secret key for webhook protection
webhook_secret = getenv('WEBHOOK_SECRET')  # NEW
if not webhook_secret:  # NEW
    raise ValueError("doesn't have WEBHOOK_SECRET")
#получения токена для бота / connect token to bot
bot=Bot(token=token)
#для удобства вывод старта работы бота / for convenience, output while bot start
print("Bot started")
#переменная app, которую ищет Vercel / the "app" variable that Vercel looks for
app = FastAPI()
#флаг, что база данных уже подключена / flag that database is already connected
db_ready = False
#подключение базы данных (один раз) / database connecting (only once)
async def ensure_db():
    global db_ready
    if not db_ready:
        await init_db()
        db_ready = True
#принимаем обновления от телеграма / receive updates from telegram
@app.post("/webhook")
async def webhook(request: Request):
    #проверяем секрет из заголовка / check secret from header
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != webhook_secret:  # NEW
        raise HTTPException(status_code=403)  # NEW
    await ensure_db()
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
#проверка, что сервер работает / check that server is running
@app.get("/")
async def health():
    return {"status": "running"}