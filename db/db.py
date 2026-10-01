import libsql_client  # NEW: замена aiosqlite / replacement for aiosqlite
from os import getenv

#адрес и токен базы берём из переменных окружения / database url and token from environment variables
def get_client():  # NEW: замена aiosqlite.connect(DB) / replacement for aiosqlite.connect(DB)
    url = getenv("TURSO_DATABASE_URL")
    token = getenv("TURSO_AUTH_TOKEN")
    if not url or not token:
        raise ValueError("doesn't have TURSO_DATABASE_URL or TURSO_AUTH_TOKEN")
    #https вместо libsql:// надёжнее для serverless / https instead of libsql:// is more stable for serverless
    url = url.replace("libsql://", "https://")
    return libsql_client.create_client(url, auth_token=token)

#создание базы данных и структуры / database and db structure creating
async def init_db() -> None:
    async with get_client() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS questions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                text TEXT NOT NULL,
                answer TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

#принимаем и добавляем запрос от пользователя / accept and add request from user
async def add_question(user_id: int, name: str, question_text: str) -> int:
    async with get_client() as db:
        rs = await db.execute(
            "INSERT INTO questions(user_id, name, text) VALUES(?,?,?)",
            [user_id, name, question_text])
        return rs.last_insert_rowid or 0

#запрашиваем id вопроса / request question id
async def get_question(qid: int):
    async with get_client() as db:
        rs = await db.execute("SELECT * FROM questions WHERE id=?", [qid])
        return rs.rows[0] if rs.rows else None

# сохраняем вопрос от пользователя / saving user question
async def save_answer(qid: int, answer: str) -> None:
    async with get_client() as db:
        await db.execute(
            "UPDATE questions SET answer=?, status='answered' WHERE id=?",
            [answer, qid])

# админ панель для списка вопросов / admin menu for list question
async def list_open():
    async with get_client() as db:
        rs = await db.execute(
            "SELECT * FROM questions WHERE status='new' ORDER BY id")
        return rs.rows