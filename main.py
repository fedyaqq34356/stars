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

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def handle_critical_error(exc_type, exc_value, exc_traceback):
    error_message = f"""🚨 КРИТИЧНА ПОМИЛКА:

Type: {exc_type.__name__}
Message: {str(exc_value)}
Traceback: {traceback.format_exc()}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, error_message)
    except:
        pass
    
    logger.critical(error_message)
    
    if RESTART_ON_ERROR:
        await safe_restart(bot)

async def on_startup():
    logger.info(f"Инициализация БД по пути: {DB_PATH}")
    init_db()
    
    try:
        import sqlite3
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT DISTINCT user_id FROM reviews WHERE user_id IS NOT NULL")
        review_users = c.fetchall()
        
        imported = 0
        for (user_id,) in review_users:
            if save_user(user_id):
                imported += 1
        
        conn.close()
        
        total_users = get_users_count()
        
        if imported > 0:
            logger.info(f"Автоматично імпортовано {imported} користувачів")
            for admin_id in ADMIN_IDS:
                await bot.send_message(
                    admin_id, 
                    f"🚀 Бот запущено!\n👥 Імпортовано: {imported}\n📊 Всього: {total_users}\n💾 БД: {DB_PATH}"
                )
        else:
            logger.info("🚀 Бот запущено успішно!")
            for admin_id in ADMIN_IDS:
                await bot.send_message(admin_id, f"🚀 Бот готовий!\n👥 Користувачів: {total_users}\n💾 БД: {DB_PATH}")
    except Exception as e:
        logger.error(f"Помилка імпорту: {e}")
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"🚀 Бот запущено (помилка імпорту: {str(e)})")

async def on_shutdown():
    logger.info("🔴 Бот завершує роботу...")
    
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, "🔴 Бот завершує роботу...")
    except Exception as e:
        logger.error(f"Помилка повідомлення адміна: {e}")

async def main():
    dp.include_router(admin_router)
    dp.include_router(payments_router)
    dp.include_router(orders_router)
    dp.include_router(reviews_router)
    dp.include_router(common_router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("🌟 Telegram Bot для продажу зірок та Telegram Premium")
    print("🚀 Запуск бота...")
    print(f"👤 Адміністратор: {ADMIN_IDS}")
    print(f"🔗 API Split: {SPLIT_API_URL}")
    print(f"📺 Канал відгуків: {REVIEWS_CHANNEL_ID}")
    print(f"🔄 Авто-перезапуск: {'✅' if RESTART_ON_ERROR else '❌'}")
    print(f"💳 Номер картки: {CARD_NUMBER}")
    print(f"💾 База даних: {DB_PATH}")
    
    if RESTART_ON_ERROR:
        sys.excepthook = lambda exc_type, exc_value, exc_traceback: asyncio.run(
            handle_critical_error(exc_type, exc_value, exc_traceback)
        )
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критична помилка: {e}")
        if RESTART_ON_ERROR:
            asyncio.run(safe_restart(bot))
        else:
            raise