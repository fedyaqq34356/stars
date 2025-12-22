import sqlite3
import logging
import os
from config import DB_PATH

logger = logging.getLogger(__name__)

def init_db():
    try:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Создана директория для БД: {db_dir}")
        
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
                user_id INTEGER PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute("PRAGMA table_info(reviews)")
        columns = [info[1] for info in c.fetchall()]
        if 'username' not in columns:
            c.execute('ALTER TABLE reviews ADD COLUMN username TEXT')
            logger.info("Добавлена колонка username в reviews")
        if 'order_id' not in columns:
            c.execute('ALTER TABLE reviews ADD COLUMN order_id TEXT')
            logger.info("Добавлена колонка order_id в reviews")

        c.execute("SELECT COUNT(*) FROM reviews WHERE id >= 322")
        conflict_count = c.fetchone()[0]
        
        if conflict_count == 0:
            c.execute("SELECT seq FROM sqlite_sequence WHERE name='reviews'")
            result = c.fetchone()
        
            if result is None:
                c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('reviews', 321)")
                logger.info("Автоинкремент для reviews установлен на 321")
            else:
                if result[0] < 321:
                    c.execute("UPDATE sqlite_sequence SET seq = 321 WHERE name = 'reviews'")
                    logger.info("Автоинкремент для reviews обновлен на 321")

        conn.commit()
        logger.info(f"База данных успешно инициализирована: {DB_PATH}")
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
        logger.info(f"Загружено {len(user_ids)} пользователей из БД")
        return user_ids
    except sqlite3.Error as e:
        logger.error(f"Ошибка при загрузке пользователей: {e}")
        return set()

def get_users_count():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        conn.close()
        logger.info(f"Всего пользователей в БД: {count}")
        return count
    except sqlite3.Error as e:
        logger.error(f"Ошибка при подсчете пользователей: {e}")
        return 0

def save_user(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        inserted = c.rowcount > 0
        conn.close()
        if inserted:
            logger.info(f"Пользователь {user_id} сохранен в базе данных")
        return inserted
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении пользователя {user_id}: {e}")
        return False

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
        logger.info(f"Отзыв #{review_id} сохранен для пользователя {user_id}")
        return review_id
    except sqlite3.Error as e:
        logger.error(f"Ошибка при сохранении отзыва: {e}")
        return None