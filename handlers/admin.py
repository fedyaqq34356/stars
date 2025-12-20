import logging
import asyncio
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import load_users, save_user
from keyboards import get_main_menu
from states import BroadcastStates
from utils import orders, safe_restart
from config import ADMIN_IDS, REVIEWS_CHANNEL_ID, RESTART_ON_ERROR

logger = logging.getLogger(__name__)
router = Router()
user_ids = load_users()

@router.message(Command("sendall"))
async def send_all_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        return
    
    text = message.text[9:].strip()
    
    if not text:
        await message.answer("📝 Використання: /sendall <текст повідомлення>")
        return
    
    success_count = 0
    fail_count = 0
    
    await message.answer(f"📡 Розпочинаю розсилку для {len(user_ids)} користувачів...")
    
    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, text)
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail_count += 1
            logger.error(f"Помилка відправки користувачу {user_id}: {e}")
    
    await message.answer(f"📊 Розсилка завершена!\n✅ Успішно: {success_count}\n❌ Помилок: {fail_count}")
    logger.info(f"Рассылка завершена: успешно {success_count}, ошибок {fail_count}")

@router.message(Command("stats"))
async def stats_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        return
    
    stats_text = f"""📊 Статистика бота:

👥 Загальна кількість користувачів: {len(user_ids)}
📋 Активних замовлень: {len(orders)}
🕒 Час роботи: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📺 Канал відгуків: {REVIEWS_CHANNEL_ID}
🔄 Авто-перезапуск: {'✅' if RESTART_ON_ERROR else '❌'}"""
    
    await message.answer(stats_text)
    logger.info(f"Администратор {message.from_user.id} запросил статистику")

@router.message(Command("migrate_users"))
async def migrate_users_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        return
    
    await message.answer("🔄 Починаю міграцію користувачів в базу даних...")
    
    migrated = 0
    for user_id in user_ids:
        save_user(user_id)
        migrated += 1
    
    await message.answer(f"✅ Міграція завершена!\n👥 Збережено користувачів: {migrated}")
    logger.info(f"Міграція завершена: {migrated} користувачів")

@router.message(Command("restart"))
async def restart_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        return
    
    await message.answer("🔄 Перезапускаю бота...")
    logger.info(f"Администратор {message.from_user.id} инициировал перезапуск")
    await safe_restart(message.bot)

@router.message(F.text == "📤 Розсилка")
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        return
    
    await message.answer("<b>📝 Введіть текст для розсилки:</b>", parse_mode="HTML")
    await state.set_state(BroadcastStates.waiting_for_broadcast_text)

@router.message(BroadcastStates.waiting_for_broadcast_text)
async def handle_broadcast_text(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас немає прав для використання цієї команди.")
        await state.clear()
        return

    text = message.text.strip()
    
    if not text:
        await message.answer("📝 Текст розсилки не може бути порожнім. Спробуйте ще раз:")
        return
    
    success_count = 0
    fail_count = 0
    
    await message.answer(f"📡 Розпочинаю розсилку для {len(user_ids)} користувачів...")
    
    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, text)
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail_count += 1
            logger.error(f"Помилка відправки користувачу {user_id}: {e}")
    
    await message.answer(f"📊 Розсилка завершена!\n✅ Успішно: {success_count}\n❌ Помилок: {fail_count}")
    logger.info(f"Рассылка завершена: успешно {success_count}, ошибок {fail_count}")
    await state.clear()