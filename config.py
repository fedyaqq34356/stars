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
    logger.error(f"Incorrect ADMIN_ID value: '{ADMIN_ID_RAW}'")
    exit(1)

SPLIT_API_TOKEN = os.getenv('SPLIT_API_TOKEN')
SPLIT_API_URL = os.getenv('SPLIT_API_URL')
REVIEWS_CHANNEL_ID = int(os.getenv('REVIEWS_CHANNEL_ID', '0'))
MAIN_CHANNEL_ID = int(os.getenv('MAIN_CHANNEL_ID', '0'))
CARD_NUMBER = os.getenv('CARD_NUMBER')
RESTART_ON_ERROR = os.getenv('RESTART_ON_ERROR', 'true').lower() == 'true'
DB_PATH = os.getenv('DB_PATH', 'bot_database.db')
VIDEO_PATH = "payment_example.mp4"

STAR_PRICE_TIERS = [
    (1,    49,    0.84),
    (50,   99,    0.92),
    (100,  1499,  0.82),
    (1500, 10000, 0.80),
]
STAR_PRICE_DEFAULT = 0.80

def get_star_price(amount: int) -> float:
    for min_qty, max_qty, price in STAR_PRICE_TIERS:
        if min_qty <= amount <= max_qty:
            return price
    return STAR_PRICE_DEFAULT

def get_star_total(amount: int) -> float:
    return round(amount * get_star_price(amount), 2)

STAR_PRICES = {
    "13⭐ – 20₴":  {"stars": 13, "price": 20,  "type": "stars"},
    "21⭐ – 30₴":  {"stars": 21, "price": 30,  "type": "stars"},
    "26⭐ – 40₴":  {"stars": 26, "price": 40,  "type": "stars"},
    "50⭐ – 46₴":  {"stars": 50, "price": get_star_total(50),  "type": "stars"},
    "3 місяці💎 – 669₴":   {"months": 3,  "price": 669,  "type": "premium"},
    "6 місяців💎 – 999₴":  {"months": 6,  "price": 999,  "type": "premium"},
    "12 місяців💎 – 1699₴": {"months": 12, "price": 1699, "type": "premium"},
}

if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    logger.error("BOT_TOKEN not set!")
    exit(1)

if not CARD_NUMBER:
    logger.error("CARD_NUMBER not set!")
    exit(1)

if not REVIEWS_CHANNEL_ID:
    logger.error("REVIEWS_CHANNEL_ID not set!")
    exit(1)