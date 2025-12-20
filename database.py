import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rating INTEGER,
                review_text TEXT,
                order_id TEXT,
                created_at TEXT,
                username TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        
        c.execute("PRAGMA table_info(reviews)")
        columns = [info[1] for info in c.fetchall()]
        if 'username' not in columns:
            c.execute('ALTER TABLE reviews ADD COLUMN username TEXT')
        if 'order_id' not in columns:
            c.execute('ALTER TABLE reviews ADD COLUMN order_id TEXT')

        c.execute("SELECT COUNT(*) FROM reviews WHERE id >= 322")
        conflict_count = c.fetchone()[0]
        
        if conflict_count == 0:
            c.execute("SELECT seq FROM sqlite_sequence WHERE name='reviews'")
            result = c.fetchone()
        
            if result is None:
                c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('reviews', 321)")
                logger.info("Автоинкремент для reviews установлен на 321 (следующий ID будет 322)")
            else:
                if result[0] < 321:
                    c.execute("UPDATE sqlite_sequence SET seq = 321 WHERE name = 'reviews'")
                    logger.info("Автоинкремент для reviews обновлен на 321 (следующий ID будет 322)")
                else:
                    logger.info(f"Автоинкремент уже установлен на {result[0]}, не изменяем")

        conn.commit()
        logger.info("База данных успешно инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
    finally:
        conn.close()

def load_users():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        user_ids = {row[0] for row in c.fetchall()}
        conn.close()
        return user_ids
    except sqlite3.Error as e:
        logger.error(f"Ошибка при загрузке пользователей: {e}")
        return set()

def save_user(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Пользователь {user_id} сохранен в базе данных")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении пользователя {user_id}: {e}")

def save_review(user_id: int, username: str, rating: int, review_text: str, order_id: str, created_at: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reviews (user_id, username, rating, review_text, order_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, rating, review_text, order_id, created_at))
        conn.commit()
        review_id = c.lastrowid
        conn.close()
        return review_id
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении отзыва: {e}")
        return None