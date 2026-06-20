import asyncio
import logging
import sys
import traceback
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, SPLIT_API_URL, REVIEWS_CHANNEL_ID, CARD_NUMBER, RESTART_ON_ERROR, DB_PATH
from database import init_db
from utils import safe_restart

from handlers.common import router as common_router
from handlers.orders import router as orders_router
from handlers.payments import router as payments_router
from handlers.reviews import router as reviews_router
from handlers.admin import router as admin_router
from handlers.profile import router as profile_router

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def handle_critical_error(exc_type, exc_value, exc_traceback):
    logger.critical(f"КРИТИЧНА ПОМИЛКА: {exc_type.__name__}: {str(exc_value)}\n{traceback.format_exc()}")
    if RESTART_ON_ERROR:
        await safe_restart(bot)

async def on_startup():
    init_db()

async def main():
    dp.include_router(admin_router)
    dp.include_router(profile_router)
    dp.include_router(payments_router)
    dp.include_router(orders_router)
    dp.include_router(reviews_router)
    dp.include_router(common_router)

    dp.startup.register(on_startup)

    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Telegram Bot for Stars & Telegram Premium")
    print("Starting bot...")
    print(f"Admins: {ADMIN_IDS}")
    print(f"Split API: {SPLIT_API_URL}")
    print(f"Reviews channel: {REVIEWS_CHANNEL_ID}")
    print(f"Auto-restart: {'ON' if RESTART_ON_ERROR else 'OFF'}")
    print(f"Card: {CARD_NUMBER}")
    print(f"DB: {DB_PATH}")

    if RESTART_ON_ERROR:
        sys.excepthook = lambda exc_type, exc_value, exc_traceback: asyncio.run(
            handle_critical_error(exc_type, exc_value, exc_traceback)
        )

    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        if RESTART_ON_ERROR:
            asyncio.run(safe_restart(bot))
        else:
            raise