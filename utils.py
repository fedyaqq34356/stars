import logging
import os
import sys
from aiogram import Bot
from config import ADMIN_IDS, MAIN_CHANNEL_ID

logger = logging.getLogger(__name__)

orders = {}

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(MAIN_CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки для пользователя {user_id}: {e}")
        return False

async def safe_restart(bot: Bot):
    logger.info("🔄 Перезапуск бота через 3 секунды...")
    await asyncio.sleep(3)
    
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, "🔄 Бот перезапускається через помилку...")
    except:
        pass
    
    os.execl(sys.executable, sys.executable, *sys.argv)