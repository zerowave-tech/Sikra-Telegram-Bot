# Sikra Agency Telegram Bot

Telegram bot for [Sikra Agency](https://sikra.agency/): turnkey digital launch for agencies and businesses (website, domain and email, campaigns, databases, CRM, forms and payments).

The bot introduces the agency, lets clients book a call in a Mini App, answers common questions, and collects custom questions into a database so the admin can reply right from Telegram.

## Features

- `/start` greeting with an inline menu: **About**, **Schedule**, **Question**
- **About**: short pitch with services and links
- **Schedule**: opens the Cal.com booking page inside Telegram as a Mini App
- **Question** menu: Cost, Services, Time, Contact, Back, Write the question
- **Write the question**: the client's question is saved to SQLite and forwarded to the admin
- **Admin replies**: the admin replies to the notification in Telegram and the answer goes back to the client
- `/questions`: list of unanswered questions (admin only)

## Tech stack

- Python 3.11+
- [aiogram 3](https://docs.aiogram.dev/) (Telegram Bot framework)
- aiosqlite (SQLite database)
- python-dotenv (configuration)
- FastAPI + uvicorn (optional, webhook mode)

## Project structure

```
.
├── main.py              # entry point (polling)
├── Routes/
│   └── Firstline.py     # handlers, keyboards, texts
├── Forms/
│   └── Form.py          # FSM states (Ask.waiting)
├── db/
│   └── db.py            # SQLite helpers (questions table)
├── .env                 # secrets (not committed)
├── .env.example
└── requirements.txt
```

Each folder (`Routes`, `Forms`, `db`) should contain an empty `__init__.py`.

## Setup

```bash
git clone <your-repo-url>
cd <project-folder>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### requirements.txt

```
aiogram>=3.13
python-dotenv
aiosqlite
fastapi
uvicorn
```

### Environment variables

Create a `.env` file in the project root (see `.env.example`):

```
BOT_TOKEN=123456:ABC-your-token
ADMIN_ID=123456789

# webhook mode only (FastAPI)
BASE_URL=https://your-domain.com
WEBHOOK_SECRET=long_random_string
API_KEY=another_long_random_string
```

- `BOT_TOKEN`: get it from [@BotFather](https://t.me/BotFather)
- `ADMIN_ID`: your numeric Telegram ID, get it from [@userinfobot](https://t.me/userinfobot). Open the bot and press `/start` once so it can message you.
- Never commit `.env`. Add it to `.gitignore`.

## Run

### Option 1: polling (simplest, good for development)

```bash
python main.py
```

### Option 2: webhook with FastAPI (production)

Telegram sends updates to your server over HTTPS, so you need a public HTTPS URL. For local testing use `ngrok http 8000` or `cloudflared tunnel` and put the generated URL in `BASE_URL`.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

This mode uses `main.py` with the FastAPI app:

```python
'''from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request,
                  x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}'''
```

Notes:

- Run a single process (no `--workers`), because FSM state is stored in memory.
- Polling and webhook cannot be used at the same time. Setting the webhook disables polling.

#### Optional: questions API

```python
'''@app.get("/api/questions")
async def api_questions(x_api_key: str | None = Header(default=None)):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return [dict(r) for r in await list_open()]'''
```

```bash
curl -H "X-API-Key: your_key" https://your-domain.com/api/questions
```

## How questions work

1. Client opens **Question** and taps **Write the question**.
2. Client sends the text. The bot saves it to `bot.db` and sends the admin a notification: `Question #N from <name>`.
3. Admin replies (Telegram **Reply**) to that notification.
4. The bot finds `#N`, sends the answer to the client and marks the question as answered.

Important: the admin must reply to the notification message itself, and must not delete or edit it.

## Database

SQLite file `bot.db`, created automatically on start.

| column     | type    | description                  |
|------------|---------|------------------------------|
| id         | INTEGER | question number              |
| user_id    | INTEGER | client's Telegram ID         |
| name       | TEXT    | client's name                |
| text       | TEXT    | question                     |
| answer     | TEXT    | admin's answer               |
| status     | TEXT    | `new` or `answered`          |
| created_at | TEXT    | creation time                |

When deploying (Docker, Railway, etc.), keep `bot.db` on a persistent volume, otherwise questions are lost on restart.

## BotFather setup

- `/mybots` > your bot > **Edit Bot** > **Edit Description**: text shown above the START button
- **Edit Commands**: `start - Start the bot`
- Optional: **Bot Settings** > **Menu Button** to open the booking page directly

## Security notes

- Keep `BOT_TOKEN` secret. If it leaks, revoke it in BotFather (**API Token** > **Revoke**).
- Admin-only handlers check `ADMIN_ID` (as an integer).
- All user text is passed through `html.escape` before being sent with `parse_mode="HTML"`.
- Webhook requests are verified with `WEBHOOK_SECRET`.

## Contacts

- Website: https://sikra.agency/
- Email: hello@sikra.agency
- Instagram: https://www.instagram.com/sikraagency/
- TikTok: https://www.tiktok.com/@sikraagency
