# Sikra Bot

Телеграм-бот агентства [Sikra](https://sikra.agency/): рассказывает об услугах, даёт записаться
на звонок и принимает вопросы от клиентов. Вопросы падают в SQLite и пересылаются админу —
админ отвечает реплаем в своём чате, ответ автоматически уходит клиенту.

Стек: Python 3.13, [aiogram 3](https://docs.aiogram.dev/), aiosqlite, python-dotenv.

---

## Возможности

**Для клиента**
- `/start` — приветствие с инлайн-кнопками: `about`, `Schedule`, `question`
- `about` — описание агентства и услуг
- `Schedule` — открывает форму записи на 30-минутный звонок (cal.com) прямо в Telegram (WebApp)
- `question` — reply-клавиатура с быстрыми ответами: `Cost`, `Services`, `Time`, `Contact`
- `Write the question` — свободный вопрос одним сообщением; уходит админу и сохраняется в базу
- Ответ админа приходит клиенту в личку

**Для админа** (только чат с `ADMIN_ID`)
- `/questions` — список неотвеченных вопросов
- Ответ реплаем на уведомление `❓ Question #N` — отправляет текст клиенту и помечает вопрос
  как `answered`

---

## Структура

```
Sikra Bot/
├── main.py              # точка входа: Dispatcher, токен, init_db, polling
├── Routes/
│   └── Firstline.py     # все хэндлеры, клавиатуры, тексты, логика ответов админа
├── Forms/
│   └── Form.py          # FSM-состояние Ask.waiting (ожидание вопроса от клиента)
├── db/
│   └── db.py            # работа с SQLite: init_db, add_question, get_question,
│                        #   save_answer, list_open
├── bot.db               # база SQLite (создаётся автоматически при первом запуске)
└── .env                 # секреты, в git не коммитится
```

### Схема базы

Таблица `questions`:

| поле         | тип     | описание                                  |
|--------------|---------|-------------------------------------------|
| `id`         | INTEGER | PK, автоинкремент — номер в `Question #N` |
| `user_id`    | INTEGER | Telegram ID автора вопроса                |
| `name`       | TEXT    | полное имя пользователя                   |
| `text`       | TEXT    | текст вопроса                             |
| `answer`     | TEXT    | ответ админа (NULL пока нет ответа)       |
| `status`     | TEXT    | `new` → `answered`                        |
| `created_at` | TEXT    | время создания (UTC, по умолчанию)        |

---

## Установка и запуск

### 1. Клонировать и создать окружение

```bash
git clone <repo-url>
cd "Sikra Bot"
python -m venv .venv
```

Активация:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install aiogram aiosqlite python-dotenv
```

> В репозитории пока нет `requirements.txt` — после установки его стоит зафиксировать:
> `pip freeze > requirements.txt`

### 3. Создать `.env` в корне проекта

```env
BOT_TOKEN=123456789:AA...ваш_токен_от_BotFather
ADMIN_ID=123456789
```

- `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather). Без него бот падает с
  `ValueError: doesn't have BOT_TOKEN`.
- `ADMIN_ID` — ваш числовой Telegram ID (узнать можно у [@userinfobot](https://t.me/userinfobot)).
  Если не задан, подставляется `0` и админские функции работать не будут.

### 4. Запустить

```bash
python main.py
```

В консоли появится `Bot started`. База `bot.db` и таблица создаются автоматически.

---

## Как это работает

1. Клиент жмёт `question` → `Write the question` — бот ставит FSM-состояние `Ask.waiting`
   и убирает клавиатуру.
2. Следующее текстовое сообщение клиента попадает в `add_question()`, состояние сбрасывается,
   клиент получает подтверждение.
3. Админу приходит сообщение вида `❓ Question #12 from Имя`.
4. Админ отвечает **реплаем** на это уведомление. Хэндлер вытаскивает номер регуляркой
   `Question #(\d+)`, шлёт текст клиенту через `bot.send_message(user_id, ...)` и вызывает
   `save_answer()`.

Весь пользовательский текст экранируется через `html.escape()` перед отправкой с
`parse_mode="HTML"`.

---

## Настройка контента

Всё редактируется в [`Routes/Firstline.py`](Routes/Firstline.py):

- `SCHEDULE_URL` — ссылка на cal.com для кнопки `Schedule` (обязательно HTTPS, иначе
  Telegram не откроет WebApp)
- `about_text` — текст кнопки `about`
- хэндлеры `cost()`, `services()`, `time_()`, `contact()` — быстрые ответы
- `first_keyboard()` / `question_keyboard()` — наборы кнопок

---

## Заметки

- `bot.db` сейчас закоммичен в репозиторий — если в нём появятся реальные обращения
  клиентов, стоит добавить `bot.db` в `.gitignore` и удалить файл из индекса
  (`git rm --cached bot.db`).
- Бот работает на long polling — вебхук не настроен, отдельный сервер/домен не нужен.
- Админ один. Для нескольких админов `ADMIN_ID` нужно переделать в список и заменить
  фильтры `F.chat.id == admin_id`.
- `/questions` показывает только вопросы со статусом `new`, отсортированные по `id`.