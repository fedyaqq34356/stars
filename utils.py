import logging
import asyncio
import os
import sys
from datetime import datetime, timedelta
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

async def cleanup_old_orders(bot: Bot):
    while True:
        try:
            current_time = datetime.now()
            to_remove = []
            
            for order_id, order in orders.items():
                order_time = datetime.fromisoformat(order['created_at'])
                if current_time - order_time > timedelta(hours=1):
                    to_remove.append(order_id)
            
            for order_id in to_remove:
                user_id = orders[order_id]['user_id']
                try:
                    from keyboards import get_main_menu
                    await bot.send_message(
                        user_id, 
                        "⏰ Ваше замовлення скасовано через тайм-аут (1 година).",
                        reply_markup=get_main_menu()
                    )
                except:
                    pass
                del orders[order_id]
                logger.info(f"Удален просроченный заказ {order_id}")
                
        except Exception as e:
            logger.error(f"Ошибка очистки заказов: {e}")
            
        await asyncio.sleep(300)

async def safe_restart(bot: Bot):
    logger.info("🔄 Перезапуск бота через 3 секунды...")
    await asyncio.sleep(3)
    
    try:
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, "🔄 Бот перезапускається через помилку...")
    except:
        pass
    
    os.execl(sys.executable, sys.executable, *sys.argv)