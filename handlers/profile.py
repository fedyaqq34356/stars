import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from database import get_user_profile, get_referral_stats, deduct_referral_balance
from keyboards import get_main_menu, get_withdrawal_keyboard, get_cancel_keyboard, get_referral_keyboard, get_withdrawal_review_keyboard
from states import WithdrawalStates
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()

REFERRAL_TEXT_TEMPLATE = (
    "🔗 <b>Реферальна система</b>\n\n"
    "💸 За кожну покупку твого друга ти отримуєш\n"
    "<b>1% від суми зірок</b> на свій баланс.\n\n"
    "👥 Запрошено друзів: <b>{referral_count}</b>\n"
    "⭐ Зірок куплено рефералами: <b>{total_referral_stars}</b>\n"
    "💰 Реферальний баланс: <b>{balance} ⭐</b>"
)

@router.message(F.text == "🔗 Реферальна система")
async def referral_handler(message: types.Message):
    user_id = message.from_user.id

    bot_info = await message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    stats = get_referral_stats(user_id)
    profile = get_user_profile(user_id)
    balance = profile['referral_balance'] if profile else 0

    text = REFERRAL_TEXT_TEMPLATE.format(
        referral_link=referral_link,
        referral_count=stats['referral_count'],
        total_referral_stars=stats['total_referral_stars'],
        balance=balance
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_referral_keyboard(referral_link))

@router.message(F.text == "💸 Вивести зірки")
async def withdraw_handler(message: types.Message):
    user_id = message.from_user.id
    profile = get_user_profile(user_id)
    stats = get_referral_stats(user_id)
    balance = profile['referral_balance'] if profile else 0

    text = (
        f"💸 <b>Вивід реферальних зірок</b>\n\n"
        f"👥 Всього рефералів: <b>{stats['referral_count']}</b>\n"
        f"⭐ Зірок куплено рефералами: <b>{stats['total_referral_stars']}</b>\n"
        f"💰 Доступно до виводу: <b>{balance} ⭐</b>\n\n"
        f"Натисни кнопку нижче, щоб розпочати вивід."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_withdrawal_keyboard())

@router.callback_query(F.data == "start_withdrawal")
async def start_withdrawal_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    profile = get_user_profile(user_id)
    balance = profile['referral_balance'] if profile else 0

    if balance <= 0:
        await callback.answer("У тебе немає зірок для виводу.", show_alert=True)
        return

    await callback.message.edit_text(
        f"🌟 Введіть кількість зірок, яку хочете вивести (мінімум 50 - 25000):\n\n"
        f"Доступно: <b>{balance}</b> зірок",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(WithdrawalStates.waiting_for_amount)
    await state.update_data(available_balance=balance)
    await callback.answer()

@router.callback_query(F.data == "cancel_withdrawal")
async def cancel_withdrawal(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Вивід скасовано.")
    await callback.answer()

@router.message(WithdrawalStates.waiting_for_amount, F.text)
async def handle_withdrawal_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    available = data.get('available_balance', 0)

    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Будь ласка, введи число.")
        return

    if amount < 50:
        await message.answer("❌ Мінімальна кількість для виводу — 50 зірок.")
        return

    if amount > 25000:
        await message.answer("❌ Максимальна кількість для виводу — 25000 зірок.")
        return

    if amount > available:
        await message.answer(f"❌ Недостатньо зірок. Доступно: {available}")
        return

    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    success = deduct_referral_balance(user_id, amount)
    if not success:
        await message.answer("❌ Помилка при виводі. Спробуй ще раз.")
        await state.clear()
        return

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"💸 Запит на вивід зірок!\n\n"
                f"👤 Користувач: {username} (ID: {user_id})\n"
                f"⭐ Кількість: {amount} зірок"
            )
        except Exception as e:
            logger.error(f"Error notifying admin {admin_id}: {e}")

    await message.answer(
        f"✅ Запит на вивід <b>{amount}</b> зірок надіслано адміністратору!\n"
        f"Очікуйте обробки.",
        parse_mode="HTML",
        reply_markup=get_main_menu(user_id)
    )

    await message.answer(
        "Будь ласка, залиш відгук про вивід:",
        reply_markup=get_withdrawal_review_keyboard()
    )

    await state.clear()
    await state.update_data(withdrawal_amount=amount, is_withdrawal_review=True)

@router.callback_query(F.data == "leave_withdrawal_review")
async def leave_withdrawal_review(callback: types.CallbackQuery, state: FSMContext):
    from keyboards import get_rating_keyboard
    from states import ReviewStates
    await callback.message.edit_text("⭐ Оцініть процес виводу:", reply_markup=get_rating_keyboard())
    await state.update_data(review_type='withdrawal')
    await state.set_state(ReviewStates.waiting_for_rating)
    await callback.answer()

@router.callback_query(F.data == "show_referral")
async def show_referral_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await callback.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    from database import get_referral_stats
    stats = get_referral_stats(user_id)
    profile = get_user_profile(user_id)
    balance = profile['referral_balance'] if profile else 0

    text = REFERRAL_TEXT_TEMPLATE.format(
        referral_link=referral_link,
        referral_count=stats['referral_count'],
        total_referral_stars=stats['total_referral_stars'],
        balance=balance
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_referral_keyboard(referral_link))
    await callback.answer()

@router.callback_query(F.data == "show_withdrawal")
async def show_withdrawal_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    from database import get_referral_stats
    profile = get_user_profile(user_id)
    stats = get_referral_stats(user_id)
    balance = profile['referral_balance'] if profile else 0
    text = (
        f"💸 <b>Вивід реферальних зірок</b>\n\n"
        f"👥 Всього рефералів: <b>{stats['referral_count']}</b>\n"
        f"⭐ Зірок куплено рефералами: <b>{stats['total_referral_stars']}</b>\n"
        f"💰 Доступно до виводу: <b>{balance} ⭐</b>\n\n"
        f"Натисни кнопку нижче, щоб розпочати вивід."
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_withdrawal_keyboard())
    await callback.answer()