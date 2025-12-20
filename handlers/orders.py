import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from keyboards import get_payment_method_keyboard, get_stars_menu
from utils import orders
from config import STAR_PRICES

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("stars_page_"))
async def handle_stars_pagination(callback: types.CallbackQuery):
    page = 2 if "page_2" in callback.data else 1
    await callback.message.edit_text(
        "<b>🎁🌟 Придбати зірки можна за такими цінами:</b>",
        reply_markup=get_stars_menu(page=page),
        parse_mode="HTML"
    )
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} переключил страницу на {page}")

@router.callback_query(F.data.startswith("select_"))
async def handle_selection(callback: types.CallbackQuery, state: FSMContext):
    selection = callback.data.replace("select_", "")
    logger.info(f"Пользователь {callback.from_user.id} выбрал пакет: {selection}")
    
    if selection not in STAR_PRICES:
        logger.error(f"Пакет {selection} не найден")
        await callback.answer("❌ Помилка: пакет не знайдено.")
        return
    
    order_data = STAR_PRICES[selection]
    
    order_id = f"{order_data['type']}_{callback.from_user.id}_{int(datetime.now().timestamp())}"
    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    
    orders[order_id] = {
        "user_id": callback.from_user.id,
        "user_name": username,
        "type": order_data["type"],
        "price": order_data["price"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    if order_data["type"] == "stars":
        orders[order_id]["stars"] = order_data["stars"]
    else:
        orders[order_id]["months"] = order_data["months"]
    
    await state.update_data(order_id=order_id)
    
    payment_text = f"""<b>💳🎅 Оберіть спосіб оплати:</b>

<i>{'⭐ Кількість зірок: ' + str(order_data['stars']) if order_data['type'] == 'stars' else '💎 Термін: ' + str(order_data['months']) + ' місяців'}</i>
<i>💰 Сума до оплати: {order_data['price']}₴</i>

<b>Доступні способи оплати:</b>
<b>💎 Оплата TON - через TON Connect</b>
<b>🇺🇦 Оплата карткою</b>"""
    
    await callback.message.edit_text(payment_text, reply_markup=get_payment_method_keyboard(order_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def cancel_order_by_user(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    if order_id and order_id in orders:
        del orders[order_id]
        logger.info(f"Заказ {order_id} delete after exit")
    await state.clear()
    await callback.message.edit_text("❌ Замовлення скасовано.")
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} отменил заказ")