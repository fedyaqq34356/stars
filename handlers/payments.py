import logging
import asyncio
import re
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from keyboards import (get_cancel_keyboard, get_main_menu, get_admin_card_approval_keyboard,
                       get_ton_connect_keyboard, get_review_keyboard)
from states import CardPaymentStates
from utils import orders
from config import CARD_NUMBER, ADMIN_IDS
from api_client import get_recipient_address, get_ton_payment_body
from database import update_user_stats, get_referrer_id, add_referral_balance, get_user_profile

logger = logging.getLogger(__name__)
router = Router()

async def send_order_to_admin(bot, order_id: str, order: dict, payment_method: str):
    order_text = (
        f"📝 Нове замовлення очікує на підтвердження:\n\n"
        f"👤 Користувач: {order['user_name']} (@{order['user_id']})\n"
        f"📦 Тип: {'Зірки' if order['type'] == 'stars' else 'Telegram Premium'}\n"
        f"{'⭐ Кількість: ' + str(order.get('stars', 'не вказано')) if order['type'] == 'stars' else '💎 Термін: ' + str(order.get('months', 'не вказано')) + ' місяців'}\n"
        f"💰 Сума: {order['price']}₴\n"
        f"💳 Спосіб оплати: {payment_method}\n"
        f"🕒 Час: {order['created_at']}\n\n"
        f"Підтвердіть або відхиліть замовлення."
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text, reply_markup=get_admin_card_approval_keyboard(order_id))
        except Exception as e:
            logger.error(f"Error sending order to admin {admin_id}: {e}")

async def send_card_order_to_admin(bot, order_id: str, order: dict):
    try:
        order_text = (
            f"💳 Новий заказ з оплатою карткою:\n\n"
            f"👤 Користувач: {order['user_name']} (ID: {order['user_id']})\n"
            f"📦 Тип: {'Зірки' if order['type'] == 'stars' else 'Telegram Premium'}\n"
            f"{'⭐ Кількість: ' + str(order.get('stars', 'не вказано')) if order['type'] == 'stars' else '💎 Термін: ' + str(order.get('months', 'не вказано')) + ' місяців'}\n"
            f"💰 Сума: {order['price']}₴\n"
            f"🕒 Час: {order['created_at']}\n\n"
            f"Скрін оплати:"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_photo(
                    admin_id,
                    photo=order['payment_screenshot'],
                    caption=order_text,
                    reply_markup=get_admin_card_approval_keyboard(order_id)
                )
            except Exception as e:
                logger.error(f"Error sending card order to admin {admin_id}: {e}")
                await bot.send_message(order['user_id'], "❌ Помилка при відправці замовлення адміністратору.",
                                       reply_markup=get_main_menu(order['user_id']))
                return
    except Exception as e:
        logger.error(f"General error in send_card_order_to_admin: {e}", exc_info=True)
        await bot.send_message(order['user_id'], "❌ Помилка при обробці замовлення.",
                               reply_markup=get_main_menu(order['user_id']))

@router.callback_query(F.data.startswith("pay_card_"))
async def handle_card_payment(callback: types.CallbackQuery, state: FSMContext):
    try:
        order_id = callback.data.replace("pay_card_", "")
        if order_id not in orders:
            await callback.message.answer("❌ Замовлення не знайдено.")
            await callback.answer()
            return

        order = orders[order_id]
        order["payment_method"] = "card"

        if order["type"] == "stars":
            payment_text = "<b>✨ Вкажіть @username (тег), на який треба відправити зірки.</b>\n\n<b>Обов'язково перевірте правильність!</b>"
        else:
            payment_text = "<b>✨ Вкажіть @username (тег), на який треба відправити Telegram Premium.</b>\n\n<b>Обов'язково перевірте правильність!</b>"

        await callback.message.answer(payment_text, parse_mode="HTML", reply_markup=get_cancel_keyboard())
        await state.update_data(order_id=order_id)
        await state.set_state(CardPaymentStates.waiting_for_username)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_card_payment: {e}")
        await callback.message.answer("❌ Помилка при обробці оплати карткою.")
        await callback.answer()

@router.message(CardPaymentStates.waiting_for_username, F.text)
async def handle_username_input(message: types.Message, state: FSMContext):
    try:
        username = message.text.strip()
        if not username:
            await message.answer("❌ Username не може бути порожнім. Спробуйте ще раз:")
            return

        if username.startswith('@'):
            username = username[1:]

        if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
            await message.answer(
                "❌ Неправильний формат username!\n\n"
                "Username повинен містити тільки латинські літери, цифри та підкреслення, довжиною від 5 до 32 символів.\n\n"
                "Спробуйте ще раз:"
            )
            return

        data = await state.get_data()
        order_id = data.get('order_id')

        if not order_id or order_id not in orders:
            await message.answer("❌ Замовлення не знайдено.")
            await state.clear()
            return

        orders[order_id]['customer_username'] = username

        if orders[order_id]["type"] == "stars":
            product_info = f"<i><b>⭐️ @{username} отримає: {orders[order_id]['stars']} ⭐️</b></i>"
        else:
            product_info = f"<i><b>💎 @{username} отримає: {orders[order_id]['months']} місяців Premium 💎</b></i>"

        await message.answer(
            f"<b>💳 Банк України</b>\n"
            f"<b>Карта:</b> <code>{CARD_NUMBER}</code>\n\n"
            f"<i><b>💰 До оплати: {orders[order_id]['price']:.2f} UAH</b></i>\n\n"
            f"<i><b>Аккаунт: @{username}</b></i>\n"
            f"{product_info}\n\n"
            f"<b>📸 Після оплати, відправте сюди в чат квитанцію оплати:</b>",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(CardPaymentStates.waiting_for_payment_screenshot)
    except Exception as e:
        logger.error(f"Error in handle_username_input: {e}", exc_info=True)
        await message.answer("❌ Помилка при обробці username.", reply_markup=get_cancel_keyboard())

@router.message(CardPaymentStates.waiting_for_payment_screenshot, F.photo)
async def handle_payment_screenshot(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        order_id = data.get('order_id')

        if order_id not in orders:
            await message.answer("❌ Замовлення не знайдено.")
            await state.clear()
            return

        orders[order_id]['payment_screenshot'] = message.photo[-1].file_id
        orders[order_id]['status'] = 'pending_admin'

        await message.answer(
            "✅ Скріншот отримано! Ваше замовлення передано адміністратору на перевірку.\n"
            "Очікуйте підтвердження (зазвичай до 30 хвилин).",
            reply_markup=get_main_menu(message.from_user.id)
        )
        await send_card_order_to_admin(message.bot, order_id, orders[order_id])
        await state.clear()
    except Exception as e:
        logger.error(f"Error processing screenshot: {e}")
        await message.answer("❌ Помилка при обробці скріншота.")
        await state.clear()

@router.message(CardPaymentStates.waiting_for_payment_screenshot, ~F.photo)
async def handle_wrong_content_type(message: types.Message):
    await message.answer("❌ Будь ласка, надішліть скріншот оплати (фото), а не текст.")

@router.callback_query(F.data.startswith("pay_ton_"))
async def handle_ton_payment(callback: types.CallbackQuery):
    order_id = callback.data.replace("pay_ton_", "")
    if order_id not in orders:
        await callback.answer("❌ Замовлення не знайдено.")
        return

    order = orders[order_id]
    if order.get("status") == "pending_admin":
        await callback.message.edit_text("Замовлення вже на розгляді у адміністратора.")
        await callback.answer()
        return

    order["payment_method"] = "ton"
    order["status"] = "pending_admin"
    await callback.message.edit_text("Очікуємо підтвердження адміністратора...")
    await send_order_to_admin(callback.bot, order_id, order, "TON")
    await callback.answer()

async def process_referral_bonus(bot, buyer_user_id: int, stars_bought: int):
    referrer_id = get_referrer_id(buyer_user_id)
    if not referrer_id or stars_bought <= 0:
        return

    bonus_stars = max(1, int(stars_bought * 0.01))
    add_referral_balance(referrer_id, bonus_stars)

    try:
        buyer_profile = get_user_profile(buyer_user_id)
        buyer_name = buyer_profile.get('full_name') or str(buyer_user_id) if buyer_profile else str(buyer_user_id)

        await bot.send_message(
            referrer_id,
            f"🎉 Твій реферал придбав {stars_bought} зірок!\n"
            f"Ти отримав {bonus_stars} зірок на реферальний баланс."
        )
    except Exception as e:
        logger.error(f"Error notifying referrer {referrer_id}: {e}")

@router.callback_query(F.data.regexp(r"^(approve|reject)_"))
async def handle_admin_approval(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("❌ У вас немає прав для цієї дії.")
            return

        action, order_id = callback.data.split("_", 1)

        if order_id not in orders:
            await callback.message.answer("❌ Замовлення не знайдено.")
            await callback.answer()
            return

        order = orders[order_id]
        user_id = order["user_id"]
        payment_method = order.get("payment_method", "card")
        is_text_message = not order.get("payment_screenshot")

        purchase_info = ""
        stars_count = 0
        if order["type"] == "stars":
            stars_count = order.get('stars', 0)
            purchase_info = f"🌟 Куплено зірок: {stars_count}\n"
        elif order["type"] == "premium":
            purchase_info = f"💎 Куплено преміум: {order.get('months', 'не вказано')} місяців\n"

        if action == "approve":
            if is_text_message:
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.message.answer("✅ Замовлення підтверджено!")
            else:
                await callback.message.edit_caption(caption=callback.message.caption, reply_markup=None)
                await callback.message.answer("✅ Оплата карткою підтверджена!")

            if payment_method == "ton":
                quantity = order["stars"] if order["type"] == "stars" else order["months"]
                username = order["user_name"]
                recipient_address = await get_recipient_address(order["type"], user_id, username, quantity)

                if not recipient_address:
                    await callback.bot.send_message(user_id, "❌ Помилка отримання адреси для оплати TON.",
                                                    reply_markup=get_main_menu(user_id))
                    await callback.answer()
                    return

                transaction_data = await get_ton_payment_body(order["type"], quantity, user_id, username)
                if not transaction_data:
                    await callback.bot.send_message(user_id, "❌ Помилка підготовки TON транзакції.",
                                                    reply_markup=get_main_menu(user_id))
                    await callback.answer()
                    return

                payment_text = (
                    f"<b>💎 Оплата через TON Connect:</b>\n\n"
                    f"<i>{'⭐ Кількість зірок: ' + str(order['stars']) if order['type'] == 'stars' else '💎 Термін: ' + str(order['months']) + ' місяців'}</i>\n"
                    f"<i>💰 Сума: {order['price']}₴</i>\n\n"
                    f"<b>📱 Натисніть кнопку нижче для оплати через TON Connect</b>"
                )
                await callback.bot.send_message(user_id, payment_text,
                                                reply_markup=get_ton_connect_keyboard(transaction_data, recipient_address),
                                                parse_mode="HTML")
            else:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                store_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔗 Перейти в магазин", url="https://split.tg/store")]
                ])
                for admin_id in ADMIN_IDS:
                    await callback.bot.send_message(admin_id, f"✅ Заказ {order_id} оброблено.",
                                                    reply_markup=store_keyboard)

                await callback.bot.send_message(
                    user_id,
                    "✅ Ваша оплата підтверджена!\n💫 Замовлення обробляється.\n\n‼️ Це займе від 5 хвилин до 2 годин.",
                    reply_markup=get_main_menu(user_id)
                )

                if order["type"] == "stars" and stars_count:
                    update_user_stats(user_id, stars_count, order.get('price', 0))
                    await process_referral_bonus(callback.bot, user_id, stars_count)

                from aiogram.fsm.storage.base import StorageKey
                review_state = FSMContext(state.storage, StorageKey(bot_id=callback.bot.id, chat_id=user_id, user_id=user_id))
                await review_state.update_data(order_id=order_id, purchase_info=purchase_info)

                await callback.bot.send_message(
                    user_id,
                    "Дякуємо за покупку! Будь ласка, залиште відгук про нашу роботу:",
                    reply_markup=get_review_keyboard()
                )

                order["status"] = "completed"

                from handlers.reviews import schedule_auto_review
                asyncio.create_task(schedule_auto_review(callback.bot, user_id, order_id, stars_count))

        else:
            if is_text_message:
                await callback.message.edit_text("❌ Заказ відхилено.")
            else:
                await callback.message.edit_caption(caption="❌ Оплата карткою відхилена.")

            await callback.bot.send_message(user_id, "❌ Ваша оплата була відхилена адміністратором.",
                                            reply_markup=get_main_menu(user_id))
            del orders[order_id]

        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_admin_approval: {e}", exc_info=True)
        await callback.answer()