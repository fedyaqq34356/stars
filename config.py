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

logger.info(f"Путь к базе данных: {DB_PATH}")
logger.info(f"Абсолютный путь к БД: {os.path.abspath(DB_PATH)}")

STAR_PRICES = {
    "50⭐ – 48₴": {"stars": 50, "price": 48, "type": "stars"},
    "60⭐ – 59₴": {"stars": 60, "price": 59, "type": "stars"},
    "70⭐ – 69₴": {"stars": 70, "price": 69, "type": "stars"},
    "80⭐ – 79₴": {"stars": 80, "price": 79, "type": "stars"},
    "90⭐ – 89₴": {"stars": 90, "price": 89, "type": "stars"},
    "100⭐ – 85₴": {"stars": 100, "price": 85, "type": "stars"},
    "200⭐ – 160₴": {"stars": 200, "price": 160, "type": "stars"},
    "300⭐ – 235₴": {"stars": 300, "price": 235, "type": "stars"},
    "400⭐ – 310₴": {"stars": 400, "price": 310, "type": "stars"},
    "500⭐ – 370₴": {"stars": 500, "price": 370, "type": "stars"},
    "1000⭐ – 735₴": {"stars": 1000, "price": 735, "type": "stars"},
    "10000⭐ – 7300₴": {"stars": 10000, "price": 7300, "type": "stars"},
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