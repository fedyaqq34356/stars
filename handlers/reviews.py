import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from keyboards import get_rating_keyboard, get_main_menu
from states import ReviewStates
from database import save_review
from utils import orders
from config import REVIEWS_CHANNEL_ID, ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == 'leave_review')
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⭐ Оцініть нашу роботу:", reply_markup=get_rating_keyboard())
    await state.set_state(ReviewStates.waiting_for_rating)
    logger.info(f"Пользователь {callback.from_user.id} начал процесс оставления отзыва")

@router.callback_query(F.data == 'skip_review')
async def skip_review(callback: types.CallbackQuery):
    await callback.message.edit_text("✅ Дякуємо за покупку! Звертайтеся ще! 🌟")
    user_id = callback.from_user.id
    for order_id, order in list(orders.items()):
        if order["user_id"] == user_id and order["status"] == "completed":
            del orders[order_id]
    logger.info(f"Пользователь {callback.from_user.id} пропустил отзыв")

@router.callback_query(F.data.startswith('rate_'), ReviewStates.waiting_for_rating)
async def handle_rating(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split('_')[1])
    await state.update_data(rating=rating)
    
    await callback.message.edit_text(f"Ваша оцінка: {'⭐' * rating}\n\n💬 Тепер напишіть текст відгуку:")
    await state.set_state(ReviewStates.waiting_for_review)
    logger.info(f"Пользователь {callback.from_user.id} выбрал оценку {rating}")

@router.message(ReviewStates.waiting_for_review)
async def handle_review_text(message: types.Message, state: FSMContext):
    try:
        review_text = message.text
        data = await state.get_data()
        rating = data.get('rating', 5)
        order_id = data.get('order_id')

        purchase_info = ""
        if order_id and order_id in orders:
            order = orders[order_id]
            if order["type"] == "stars":
                purchase_info = f"🌟 Куплено зірок: {order.get('stars', 'не указано')}\n"
            elif order["type"] == "premium":
                purchase_info = f"💎 Куплено преміум: {order.get('months', 'не указано')} місяців\n"
        else:
            purchase_info = data.get('purchase_info', '')
            
            if not purchase_info and order_id:
                try:
                    parts = order_id.split('_')
                    if len(parts) >= 3:
                        order_type = parts[0]
                        if order_type == "stars":
                            purchase_info = "🌟 Куплено зірок: не вказано\n"
                        elif order_type == "premium":
                            purchase_info = "💎 Куплено преміум: не вказано\n"
                except Exception as e:
                    logger.error(f"Ошибка при восстановлении информации: {e}")

        if not purchase_info:
            purchase_info = "🛒 Покупка в нашому боті\n"

        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        review_id = save_review(
            message.from_user.id,
            username,
            rating,
            review_text,
            order_id,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        if not review_id:
            await message.answer(
                "❌ Помилка при збереженні відгуку.",
                reply_markup=get_main_menu(message.from_user.id)
            )
            await state.clear()
            return

        channel_message = f"""⭐☃️НОВИЙ ВІДГУК #{review_id} ⭐

👤 Користувач: {message.from_user.full_name}
📱 Username: @{message.from_user.username if message.from_user.username else 'не вказано'}
{purchase_info}🌟 Оцінка: {'⭐' * rating}
📝 Відгук: {review_text}

📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#відгук #зірки #телеграм"""
        
        try:
            await message.bot.send_message(REVIEWS_CHANNEL_ID, channel_message)
        except Exception as e:
            logger.error(f"Ошибка при отправке отзыва в канал: {e}")
            await message.answer(
                "❌ Помилка при публікації відгуку в канал.",
                reply_markup=get_main_menu(message.from_user.id)
            )
            await state.clear()
            return

        await message.answer(
            "✅ Дякуємо за відгук! Він опубліковано в нашому каналі відгуків.",
            reply_markup=get_main_menu(message.from_user.id)
        )

        for admin_id in ADMIN_IDS:
            admin_message = f"💬 Новий відгук #{review_id} від {message.from_user.full_name} ({rating}/5 зірок)\n{purchase_info.strip()}"
            await message.bot.send_message(admin_id, admin_message)

        if order_id and order_id in orders:
            del orders[order_id]

    except Exception as e:
        logger.error(f"Ошибка в handle_review_text: {str(e)}", exc_info=True)
        await message.answer(
            "❌ Помилка при обробці відгуку.",
            reply_markup=get_main_menu(message.from_user.id)
        )
    
    finally:
        await state.clear()