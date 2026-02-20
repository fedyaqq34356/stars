import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from keyboards import get_payment_method_keyboard, get_confirm_order_keyboard, get_cancel_keyboard
from utils import orders
from config import STAR_PRICES, get_star_price, get_star_total
from states import StarsOrderStates

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "custom_stars_amount")
async def custom_stars_amount_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>🌟 Введіть суму зірок, яку хочете купити:</b>\n\n"
        "<i>💰 Тарифи:\n"
        "1–49 зірок → 0.84₴/шт\n"
        "50–99 зірок → 0.92₴/шт\n"
        "100–1499 зірок → 0.82₴/шт\n"
        "1500+ зірок → 0.80₴/шт</i>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(StarsOrderStates.waiting_for_stars_amount)
    await callback.answer()

@router.message(StarsOrderStates.waiting_for_stars_amount, F.text)
async def handle_stars_amount_input(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())

        if amount <= 0:
            await message.answer("❌ Кількість зірок повинна бути більше нуля. Спробуйте ще раз:")
            return

        if amount > 100000:
            await message.answer("❌ Максимальна кількість зірок - 100000. Спробуйте ще раз:")
            return

        rate = get_star_price(amount)
        price = get_star_total(amount)
        await state.update_data(stars=amount, price=price)

        confirm_text = (
            f"<b>📋 Підтвердіть замовлення:</b>\n\n"
            f"<b>⭐ Кількість зірок:</b> {amount}\n"
            f"<b>💰 Курс:</b> {rate}₴ за зірку\n"
            f"<b>💵 Вартість:</b> {price}₴\n\n"
            f"<b>Підтвердити замовлення?</b>"
        )
        await message.answer(confirm_text, reply_markup=get_confirm_order_keyboard(), parse_mode="HTML")

    except ValueError:
        await message.answer("❌ Будь ласка, введіть число. Спробуйте ще раз:")

@router.callback_query(F.data == "confirm_stars_order")
async def confirm_stars_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    stars = data.get('stars')
    price = data.get('price')

    if not stars or not price:
        await callback.answer("❌ Помилка: дані замовлення не знайдено.")
        await state.clear()
        return

    order_id = f"stars_{callback.from_user.id}_{int(datetime.now().timestamp())}"
    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    orders[order_id] = {
        "user_id": callback.from_user.id,
        "user_name": username,
        "type": "stars",
        "stars": stars,
        "price": price,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    await state.update_data(order_id=order_id)

    payment_text = (
        f"<b>💳 Оберіть спосіб оплати:</b>\n\n"
        f"<i>⭐ Кількість зірок: {stars}</i>\n"
        f"<i>💰 Сума до оплати: {price}₴</i>\n\n"
        f"<b>Доступні способи оплати:</b>\n"
        f"<b>💎 Оплата TON - через TON Connect</b>\n"
        f"<b>🇺🇦 Оплата карткою</b>"
    )

    await callback.message.edit_text(payment_text, reply_markup=get_payment_method_keyboard(order_id), parse_mode="HTML")
    await callback.answer()
    await state.clear()

@router.callback_query(F.data == "cancel_stars_order")
async def cancel_stars_order(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Замовлення скасовано.")
    await callback.answer()

@router.callback_query(F.data.startswith("select_"))
async def handle_selection(callback: types.CallbackQuery, state: FSMContext):
    selection = callback.data.replace("select_", "")
    logger.info(f"User {callback.from_user.id} selected package: {selection}")

    if selection not in STAR_PRICES:
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

    if order_data["type"] == "stars":
        payment_text = (
            f"<b>💳 Оберіть спосіб оплати:</b>\n\n"
            f"<i>⭐ Кількість зірок: {order_data['stars']}</i>\n"
            f"<i>💰 Сума до оплати: {order_data['price']}₴</i>\n\n"
            f"<b>Доступні способи оплати:</b>\n"
            f"<b>💎 Оплата TON - через TON Connect</b>\n"
            f"<b>🇺🇦 Оплата карткою</b>"
        )
    else:
        payment_text = (
            f"<b>💳 Оберіть спосіб оплати:</b>\n\n"
            f"<i>💎 Термін: {order_data['months']} місяців</i>\n"
            f"<i>💰 Сума до оплати: {order_data['price']}₴</i>\n\n"
            f"<b>Доступні способи оплати:</b>\n"
            f"<b>💎 Оплата TON - через TON Connect</b>\n"
            f"<b>🇺🇦 Оплата карткою</b>"
        )

    await callback.message.edit_text(payment_text, reply_markup=get_payment_method_keyboard(order_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "cancel_order")
async def cancel_order_by_user(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id')
    if order_id and order_id in orders:
        del orders[order_id]
    await state.clear()
    await callback.message.edit_text("❌ Замовлення скасовано.")
    await callback.answer()