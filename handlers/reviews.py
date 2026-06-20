import logging
import asyncio
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from keyboards import get_rating_keyboard, get_main_menu
from states import ReviewStates
from database import save_review, save_silent_review, get_user_profile
from utils import orders
from config import REVIEWS_CHANNEL_ID, ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()

pending_auto_reviews: dict = {}

async def schedule_auto_review(bot, user_id: int, order_id: str, stars_count: int):
    key = f"{user_id}_{order_id}"
    pending_auto_reviews[key] = True

    await asyncio.sleep(3600)

    if pending_auto_reviews.get(key):
        del pending_auto_reviews[key]
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        review_id = save_silent_review(user_id, order_id, created_at)
        if review_id:
            try:
                try:
                    chat = await bot.get_chat(user_id)
                    user_name = chat.full_name or str(user_id)
                except Exception:
                    profile = get_user_profile(user_id)
                    user_name = (profile.get('full_name') if profile else None) or str(user_id)
                stars_line = f"✨ Куплено зірок: {stars_count}\n" if stars_count else ""
                channel_message = (
                    f"⭐ НОВИЙ ВІДГУК #{review_id} ⭐\n\n"
                    f"🆔 Користувач: {user_name}\n"
                    f"{stars_line}"
                    f"📝 Відгук: вирішив промовчати..\n"
                    f"📅 Дата: {created_at}\n\n"
                    f"#відгук #зірки #телеграм"
                )
                await bot.send_message(REVIEWS_CHANNEL_ID, channel_message)
            except Exception as e:
                logger.error(f"Auto-review posting error: {e}")

def cancel_auto_review(user_id: int, order_id: str):
    key = f"{user_id}_{order_id}"
    if key in pending_auto_reviews:
        pending_auto_reviews[key] = False

@router.callback_query(F.data == 'leave_review')
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id', '')
    user_id = callback.from_user.id

    for o_id, order in orders.items():
        if order.get('user_id') == user_id and order.get('status') == 'completed':
            cancel_auto_review(user_id, o_id)
            break
    cancel_auto_review(user_id, order_id)

    await callback.message.edit_text("⭐ Оцініть нашу роботу:", reply_markup=get_rating_keyboard())
    await state.set_state(ReviewStates.waiting_for_rating)

@router.callback_query(F.data == 'skip_review')
async def skip_review(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ Дякуємо за покупку! Звертайтеся ще!")
    user_id = callback.from_user.id
    for order_id, order in list(orders.items()):
        if order["user_id"] == user_id and order["status"] == "completed":
            del orders[order_id]

@router.callback_query(F.data.startswith('rate_'), ReviewStates.waiting_for_rating)
async def handle_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split('_')[1])
    await state.update_data(rating=rating)
    await callback.message.edit_text(f"Ваша оцінка: {'⭐' * rating}\n\n💬 Тепер напишіть текст відгуку:")
    await state.set_state(ReviewStates.waiting_for_review)

@router.message(ReviewStates.waiting_for_review)
async def handle_review_text(message: types.Message, state: FSMContext):
    try:
        review_text = message.text
        data = await state.get_data()
        rating = data.get('rating', 5)
        order_id = data.get('order_id')
        review_type = data.get('review_type', 'purchase')

        purchase_info = ""
        if order_id and order_id in orders:
            order = orders[order_id]
            if order["type"] == "stars":
                purchase_info = f"✨ Куплено зірок: {order.get('stars', 'не вказано')}\n"
            elif order["type"] == "premium":
                purchase_info = f"💎 Куплено преміум: {order.get('months', 'не вказано')} місяців\n"
        else:
            purchase_info = data.get('purchase_info', '')
            if not purchase_info and order_id:
                try:
                    parts = order_id.split('_')
                    if parts[0] == "stars":
                        purchase_info = "✨ Куплено зірок: не вказано\n"
                    elif parts[0] == "premium":
                        purchase_info = "💎 Куплено преміум: не вказано\n"
                except Exception:
                    pass

        if not purchase_info:
            purchase_info = "🛒 Покупка в нашому боті\n"

        user_full_name = message.from_user.full_name or message.from_user.username or str(message.from_user.id)
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        review_id = save_review(
            message.from_user.id,
            username,
            rating,
            review_text,
            order_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            review_type
        )

        if not review_id:
            await message.answer("❌ Помилка при збереженні відгуку.", reply_markup=get_main_menu(message.from_user.id))
            await state.clear()
            return

        review_label = "ВІДГУК ПРО ВИВІД" if review_type == 'withdrawal' else "НОВИЙ ВІДГУК"

        channel_message = (
            f"⭐ {review_label} #{review_id} ⭐\n\n"
            f"🆔 Користувач: {user_full_name}\n"
            f"{purchase_info}"
            f"🌟 Оцінка: {'⭐' * rating}\n"
            f"📝 Відгук: {review_text}\n\n"
            f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"#відгук #зірки #телеграм"
        )

        try:
            await message.bot.send_message(REVIEWS_CHANNEL_ID, channel_message)
        except Exception as e:
            logger.error(f"Error posting review to channel: {e}")
            await message.answer("❌ Помилка при публікації відгуку.", reply_markup=get_main_menu(message.from_user.id))
            await state.clear()
            return

        await message.answer("✅ Дякуємо за відгук! Він опубліковано в нашому каналі відгуків.",
                             reply_markup=get_main_menu(message.from_user.id))

        for admin_id in ADMIN_IDS:
            await message.bot.send_message(
                admin_id,
                f"💬 Новий відгук #{review_id} від {message.from_user.full_name} ({rating}/5 зірок)\n{purchase_info.strip()}"
            )

        if order_id and order_id in orders:
            del orders[order_id]

    except Exception as e:
        logger.error(f"Error in handle_review_text: {e}", exc_info=True)
        await message.answer("❌ Помилка при обробці відгуку.", reply_markup=get_main_menu(message.from_user.id))
    finally:
        await state.clear()