import aiosqlite

DB = "bot.db"

#создание базы данных и структуры / database and db structure creating
async def init_db() -> None:
    async with aiosqlite.connect(DB) as db:
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
        await db.commit()

#принимаем и добавляем запрос от пользователя / accept and add request from user
async def add_question(user_id: int, name: str, question_text: str) -> int:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "INSERT INTO questions(user_id, name, text) VALUES(?,?,?)",
            (user_id, name, question_text))
        await db.commit()
        return cur.lastrowid or 0

#запрашиваем id вопроса / request question id
async def get_question(qid: int):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM questions WHERE id=?", (qid,))
        return await cur.fetchone()

# сохраняем вопрос от пользователя / saving user question
async def save_answer(qid: int, answer: str) -> None:
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE questions SET answer=?, status='answered' WHERE id=?",
            (answer, qid))
        await db.commit()

# админ панель для списка вопросов / admin menu for list question
async def list_open():
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM questions WHERE status='new' ORDER BY id")
        return await cur.fetchall()