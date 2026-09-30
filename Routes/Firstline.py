from aiogram.types import Message, CallbackQuery, WebAppInfo, LinkPreviewOptions
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from db.db import add_question, get_question, save_answer, list_open
from Forms.Form import Ask
import re
from html import escape
from os import getenv
from dotenv import load_dotenv
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
)
load_dotenv()
admin_id = int(getenv('ADMIN_ID', "0") )  # Telegram ID
#подключение файла к диспатчеру / connect file to Dispatcher
router = Router()
#переменная для команды записи / variable for Inline command schedule
SCHEDULE_URL = "https://cal.com/sikra-agency/30min"


# стартовая команда / starting command
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(f"<code>Hi dear!</code>\n whats you "
                     f"interested in?", reply_markup=(first_keyboard()),parse_mode='HTML' )

# Клиент присылает текст, в базу и админу / client send the question,a to database and admin
@router.message(Ask.waiting, F.text)
async def got_question(msg: Message, state: FSMContext, bot: Bot):
    if msg.from_user is None or msg.text is None:
        return
    name = msg.from_user.full_name
    qid = await add_question(msg.from_user.id, name, msg.text)
    await state.clear()

    await msg.answer("Thanks! We'll answer you here as soon as possible ✅",
                     reply_markup=first_keyboard())
    await bot.send_message(
        admin_id,
        f"❓ <b>Question #{qid}</b> from {escape(name)}\n\n"
        f"{escape(msg.text)}\n\n"
        f"<i>Reply to this message to answer.</i>", parse_mode="HTML")

#все команды для категории question(replykeyboard) / all command for question(replykeyboard)
@router.message(F.text == "Cost")
async def cost(msg: Message):
    await msg.answer("Pricing depends on the scope. Book a call and we'll propose a plan.")

@router.message(F.text == "Services")
async def services(msg: Message):
    await msg.answer("Website, domain & email, campaigns, databases, CRM, forms and payments.")

@router.message(F.text == "Time")
async def time_(msg: Message):
    await msg.answer("Timelines depend on the scope. We'll agree on them after the first call.")

@router.message(F.text == "Contact")
async def contact(msg: Message):
    await msg.answer("✉️ hello@sikra.agency\n🌐 https://sikra.agency/\n or write our social media\n"
          "https://instagram.com/sikraagency/,\n https://tiktok.com@sikra.agency/")

@router.message(F.text == "⬅️ Back")
async def back(msg: Message):
    await msg.answer("Choose an option:", reply_markup=first_keyboard())

 #Клиент нажимает "Write the question"
@router.message(F.text == "Write the question")
async def ask(msg: Message, state: FSMContext):
    await state.set_state(Ask.waiting)
    await msg.answer("Write your question in one message 👇",
                     reply_markup=ReplyKeyboardRemove())



# Список неотвеченных / list of not answered question
@router.message(Command("questions"), F.chat.id == admin_id)
async def open_questions(msg: Message):
    rows = await list_open()
    if not rows:
        await msg.answer("No open questions")
        return
    await msg.answer("\n\n".join(
        f"#{r['id']} {escape(r['name'])}: {escape(r['text'])}" for r in rows), parse_mode='HTML')

#функция для кнопок у текста приветствия / action button
def first_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text="about",callback_data="about")],
        [InlineKeyboardButton(text="Schedule", web_app=WebAppInfo(url=SCHEDULE_URL))],
        [InlineKeyboardButton(text="question",callback_data="question")],
    ]
    )
    return keyboard

#клавиатура для question опции / keyboard for question option
def question_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Cost")],[KeyboardButton(text="Services")],
            [KeyboardButton(text="Time")],[KeyboardButton(text="Contact")],
            [KeyboardButton(text="⬅️ Back")],[KeyboardButton(text="Write the question")]
        ],
        resize_keyboard=True,
    )
    return keyboard

#переменная для кнопки about / variable for about button
about_text= (
    "<b>Sikra Agency</b>\n"
    "<i>When an idea is born, a spark ignites. We build everything around it.</i>\n\n"
    "Launching an agency or a business means a hundred technical decisions "
    "before your first client. We take them all off your plate: "
    "one team, one setup, ready to work.\n\n"
    " <b>What we set up</b>\n"
    " <b>Website</b>: structure, copy, design, live on your own domain\n"
    " <b>Domain &amp; work email</b>: name@your-company with SPF, DKIM and DMARC, so mail stays out of spam\n"
    " <b>Email campaigns</b>: templates, automated sequences, delivery and open reports\n"
    " <b>Databases</b>: clients, orders and history in one place, with backups\n"
    " <b>CRM</b>: deal stages, tasks and reminders shaped around your services\n"
    " <b>Forms</b>: enquiries from your site land straight in CRM and inbox\n"
    " <b>Payments &amp; receipts</b>: processing, invoices and receipts to clients\n\n"
    "🔗 <a href=\"https://sikra.agency/\">sikra.agency</a>  ·  "
    "✉️ hello@sikra.agency\n"
    " <a href=\"https://www.instagram.com/sikraagency/\">Instagram</a>  ·  "
    " <a href=\"https://www.tiktok.com/@sikraagency\">TikTok</a>\n\n"
    "<b>Ready to launch? Tap «Schedule» and tell us about your business!</b>"
)
#каллбек для кнопки about для вывода текста / callback function for text output
@router.callback_query(lambda c: c.data == "about")
async def about(call: CallbackQuery):
    if isinstance(call.message, Message):
        await call.message.answer(
            about_text, parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    await call.answer()
#каллбек для кнопки question / callback function for question button
@router.callback_query(lambda c: c.data== "question")
async def question(call: CallbackQuery):
    if isinstance(call.message, Message):
        await call.message.answer(
            "What do you want to know?",
            reply_markup=question_keyboard(),
        )
    await call.answer()


# 3. админ отвечает реплаем на уведомление, ответ уходит клиенту
@router.message(F.chat.id == admin_id, F.reply_to_message, F.text)
async def admin_answer(msg: Message, bot: Bot) -> None:
    if msg.reply_to_message is None or msg.text is None:
        return
    m = re.search(r"Question #(\d+)", msg.reply_to_message.text or "")
    if m is None:
        return
    q = await get_question(int(m.group(1)))
    if q is None:
        await msg.answer("Question not found")
        return
    await bot.send_message(
        q["user_id"],
        f"💬 <b>Answer to your question:</b>\n\n{escape(msg.text)}",
        parse_mode="HTML",
    )
    await save_answer(q["id"], msg.text)
    await msg.answer("✅ Sent")



