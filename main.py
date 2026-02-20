import asyncio
import logging
import sys
import traceback
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, SPLIT_API_URL, REVIEWS_CHANNEL_ID, CARD_NUMBER, RESTART_ON_ERROR, DB_PATH
from database import init_db, get_users_count, save_user
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
    error_message = (
        f"КРИТИЧНА ПОМИЛКА:\n\n"
        f"Type: {exc_type.__name__}\n"
        f"Message: {str(exc_value)}\n"
        f"Traceback: {traceback.format_exc()}\n\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, error_message)
    except Exception:
        pass

    logger.critical(error_message)

    if RESTART_ON_ERROR:
        await safe_restart(bot)

async def on_startup():
    logger.info(f"Initializing DB: {DB_PATH}")
    init_db()

    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT DISTINCT user_id FROM reviews WHERE user_id IS NOT NULL")
        review_users = c.fetchall()
        conn.close()

        imported = 0
        for (user_id,) in review_users:
            if save_user(user_id):
                imported += 1

        total_users = get_users_count()

        if imported > 0:
            logger.info(f"Auto-imported {imported} users")
            for admin_id in ADMIN_IDS:
                await bot.send_message(admin_id, f"Bot started!\nImported: {imported}\nTotal: {total_users}\nDB: {DB_PATH}")
        else:
            logger.info("Bot started successfully!")
            for admin_id in ADMIN_IDS:
                await bot.send_message(admin_id, f"Bot ready!\nUsers: {total_users}\nDB: {DB_PATH}")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"Bot started (startup error: {str(e)})")

async def on_shutdown():
    logger.info("Bot shutting down...")
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, "Bot shutting down...")
    except Exception as e:
        logger.error(f"Shutdown notify error: {e}")

async def main():
    dp.include_router(admin_router)
    dp.include_router(profile_router)
    dp.include_router(payments_router)
    dp.include_router(orders_router)
    dp.include_router(reviews_router)
    dp.include_router(common_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

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