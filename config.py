import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID_RAW = os.getenv('ADMIN_ID', '0')

try:
    ADMIN_IDS = [int(x.strip()) for x in ADMIN_ID_RAW.split(",") if x.strip()]
except ValueError:
    logger.error(f"❌ Некорректное значение ADMIN_ID: '{ADMIN_ID_RAW}'")
    exit(1)

SPLIT_API_TOKEN = os.getenv('SPLIT_API_TOKEN')
SPLIT_API_URL = os.getenv('SPLIT_API_URL')
REVIEWS_CHANNEL_ID = int(os.getenv('REVIEWS_CHANNEL_ID', '0'))
MAIN_CHANNEL_ID = int(os.getenv('MAIN_CHANNEL_ID', '0'))
CARD_NUMBER = os.getenv('CARD_NUMBER')
RESTART_ON_ERROR = os.getenv('RESTART_ON_ERROR', 'true').lower() == 'true'
DB_PATH = os.getenv('DB_PATH', 'bot_database.db')
VIDEO_PATH = "payment_example.mp4"

STAR_PRICE_PER_UNIT = 0.84

logger.info(f"Путь к базе данных: {DB_PATH}")
logger.info(f"Абсолютный путь к БД: {os.path.abspath(DB_PATH)}")

STAR_PRICES = {
    "13⭐ – 11₴": {"stars": 13, "price": round(13 * STAR_PRICE_PER_UNIT, 2), "type": "stars"},
    "21⭐ – 18₴": {"stars": 21, "price": round(21 * STAR_PRICE_PER_UNIT, 2), "type": "stars"},
    "26⭐ – 22₴": {"stars": 26, "price": round(26 * STAR_PRICE_PER_UNIT, 2), "type": "stars"},
    "50⭐ – 42₴🔥": {"stars": 50, "price": round(50 * STAR_PRICE_PER_UNIT, 2), "type": "stars"},
    "3 місяці💎 – 669₴": {"months": 3, "price": 669, "type": "premium"},
    "6 місяців💎 – 999₴": {"months": 6, "price": 999, "type": "premium"},
    "12 місяців💎 – 1699₴": {"months": 12, "price": 1699, "type": "premium"},
}

if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logger.error("❌ BOT_TOKEN не встановлено!")
    exit(1)

if not CARD_NUMBER:
    logger.error("❌ CARD_NUMBER не встановлено!")
    exit(1)

if not REVIEWS_CHANNEL_ID:
    logger.error("❌ REVIEWS_CHANNEL_ID не встановлено!")
    exit(1)