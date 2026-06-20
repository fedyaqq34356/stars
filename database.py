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
                username TEXT,
                review_type TEXT DEFAULT 'purchase'
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                full_name TEXT,
                total_stars INTEGER DEFAULT 0,
                total_uah REAL DEFAULT 0,
                referral_balance INTEGER DEFAULT 0,
                referred_by INTEGER
            )
        ''')

        c.execute("PRAGMA table_info(reviews)")
        review_cols = [info[1] for info in c.fetchall()]
        if 'username' not in review_cols:
            c.execute('ALTER TABLE reviews ADD COLUMN username TEXT')
        if 'order_id' not in review_cols:
            c.execute('ALTER TABLE reviews ADD COLUMN order_id TEXT')
        if 'review_type' not in review_cols:
            c.execute('ALTER TABLE reviews ADD COLUMN review_type TEXT DEFAULT \'purchase\'')

        c.execute("PRAGMA table_info(users)")
        user_cols = [info[1] for info in c.fetchall()]
        for col, col_type in [('username', 'TEXT'), ('full_name', 'TEXT'),
                               ('total_stars', 'INTEGER DEFAULT 0'),
                               ('total_uah', 'REAL DEFAULT 0'),
                               ('referral_balance', 'INTEGER DEFAULT 0'),
                               ('referred_by', 'INTEGER')]:
            if col not in user_cols:
                c.execute(f'ALTER TABLE users ADD COLUMN {col} {col_type}')

        c.execute("SELECT COUNT(*) FROM reviews WHERE id >= 603")
        conflict_count = c.fetchone()[0]

        if conflict_count == 0:
            c.execute("SELECT seq FROM sqlite_sequence WHERE name='reviews'")
            result = c.fetchone()
            if result is None:
                c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('reviews', 602)")
            else:
                if result[0] < 602:
                    c.execute("UPDATE sqlite_sequence SET seq = 602 WHERE name = 'reviews'")

        c.execute("UPDATE users SET total_stars = 0 WHERE total_stars IS NULL")
        c.execute("UPDATE users SET total_uah = 0 WHERE total_uah IS NULL")
        c.execute("UPDATE users SET referral_balance = 0 WHERE referral_balance IS NULL")

        conn.commit()
        logger.info(f"Database initialized: {DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"DB init error: {e}")
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
        logger.error(f"Error loading users: {e}")
        return set()

def get_users_count():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        conn.close()
        return count
    except sqlite3.Error as e:
        logger.error(f"Error counting users: {e}")
        return 0

def save_user(user_id: int, username: str = None, full_name: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                  (user_id, username, full_name))
        if username or full_name:
            c.execute("UPDATE users SET username=COALESCE(?, username), full_name=COALESCE(?, full_name) WHERE user_id=?",
                      (username, full_name, user_id))
        conn.commit()
        inserted = c.rowcount > 0
        conn.close()
        return inserted
    except sqlite3.Error as e:
        logger.error(f"Error saving user {user_id}: {e}")
        return False

def set_referrer(user_id: int, referrer_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row and row[0] is None:
            c.execute("UPDATE users SET referred_by=? WHERE user_id=?", (referrer_id, user_id))
            conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Error setting referrer: {e}")

def get_user_profile(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, username, full_name, COALESCE(total_stars,0), COALESCE(total_uah,0), COALESCE(referral_balance,0), referred_by FROM users WHERE user_id=?",
                  (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'total_stars': row[3] or 0,
                'total_uah': row[4] or 0,
                'referral_balance': row[5] or 0,
                'referred_by': row[6]
            }
        return None
    except sqlite3.Error as e:
        logger.error(f"Error getting profile: {e}")
        return None

def update_user_stats(user_id: int, stars: int, uah: float):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET total_stars = COALESCE(total_stars, 0) + ?, total_uah = COALESCE(total_uah, 0) + ? WHERE user_id=?",
                  (stars, uah, user_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Error updating stats: {e}")

def get_referrer_id(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.Error as e:
        logger.error(f"Error getting referrer: {e}")
        return None

def add_referral_balance(user_id: int, stars: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, referral_balance) VALUES (?, 0)", (user_id,))
        c.execute("UPDATE users SET referral_balance = COALESCE(referral_balance, 0) + ? WHERE user_id=?",
                  (stars, user_id))
        rows_affected = c.rowcount
        conn.commit()
        conn.close()
        if rows_affected == 0:
            logger.error(f"add_referral_balance: user {user_id} still not found after insert!")
        else:
            logger.info(f"add_referral_balance: +{stars} stars to user {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Error adding referral balance: {e}")

def deduct_referral_balance(user_id: int, stars: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COALESCE(referral_balance, 0) FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row or row[0] < stars:
            conn.close()
            return False
        c.execute("UPDATE users SET referral_balance = COALESCE(referral_balance, 0) - ? WHERE user_id=?",
                  (stars, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error deducting referral balance: {e}")
        return False

def get_referral_stats(user_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,))
        count = c.fetchone()[0]
        c.execute("SELECT SUM(total_stars) FROM users WHERE referred_by=?", (user_id,))
        total = c.fetchone()[0] or 0
        conn.close()
        return {'referral_count': count, 'total_referral_stars': total}
    except sqlite3.Error as e:
        logger.error(f"Error getting referral stats: {e}")
        return {'referral_count': 0, 'total_referral_stars': 0}

def save_review(user_id: int, username: str, rating: int, review_text: str, order_id: str, created_at: str, review_type: str = 'purchase'):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reviews (user_id, username, rating, review_text, order_id, created_at, review_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, rating, review_text, order_id, created_at, review_type))
        conn.commit()
        review_id = c.lastrowid
        conn.close()
        return review_id
    except sqlite3.Error as e:
        logger.error(f"Error saving review: {e}")
        return None

def save_silent_review(user_id: int, order_id: str, created_at: str) -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reviews (user_id, username, rating, review_text, order_id, created_at, review_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, None, None, None, order_id, created_at, 'silent'))
        conn.commit()
        review_id = c.lastrowid
        conn.close()
        return review_id
    except sqlite3.Error as e:
        logger.error(f"Error saving silent review: {e}")
        return None