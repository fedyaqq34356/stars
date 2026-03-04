import logging
import random
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import save_user, set_referrer, get_user_profile
from keyboards import get_main_menu, get_stars_menu, get_premium_menu, get_subscription_keyboard, get_profile_keyboard, get_star_rate_keyboard
from utils import check_subscription, orders
from config import ADMIN_IDS, STAR_PRICE_TIERS, STAR_PRICE_DEFAULT
from states import StarsOrderStates

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

async def subscription_required(message, bot) -> bool:
    if not await check_subscription(bot, message.from_user.id):
        subscription_text = "Щоб користуватися ботом, потрібно підписатися на наш основний канал!\n\nПідпишіться на канал і натисніть кнопку \"Перевірити підписку\""
        await bot.send_message(
            message.from_user.id,
            subscription_text,
            reply_markup=get_subscription_keyboard()
        )
        return False
    return True

async def clear_user_state(state: FSMContext, user_id: int):
    current_state = await state.get_state()
    if current_state:
        data = await state.get_data()
        order_id = data.get('order_id')
        if order_id and order_id in orders:
            del orders[order_id]
        await state.clear()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    save_user(user_id, username, full_name)

    await clear_user_state(state, user_id)

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user_id:
                set_referrer(user_id, referrer_id)
        except ValueError:
            pass

    if not await subscription_required(message, message.bot):
        return

    welcome_text = """<b>🌟 Ласкаво просимо до @ZEMSTA_stars_bot!</b>
<b>✨ Обирай, купуй і користуйся зірками!</b>

<b>🎁 Економія до 30%!</b>

<b>💎 Оплата ₴.</b>

<b>👇 Натисни кнопки нижче і починай!</b>"""

    try:
        photo = types.FSInputFile('welcome_image.jpg')
        await message.answer_photo(photo, caption=welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")
    except FileNotFoundError:
        await message.answer(welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await message.answer(welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")

    logger.info(f"User {user_id} started bot")

@router.message(Command("help"))
async def help_command(message: types.Message):
    help_text = """📋 Як купити зірки або Telegram Premium:

1️⃣ Оберіть "Придбати зірки" або "Придбати Telegram Premium" у меню
2️⃣ Виберіть потрібний пакет
3️⃣ Оберіть спосіб оплати (TON або карткою)
4️⃣ Очікуйте підтвердження адміністратора
5️⃣ Для оплати TON: підтвердіть транзакцію в гаманці.
Для оплати карткою: надішліть username, а потім скриншот оплати.
6️⃣ Очікуйте автоматичного зарахування зірок або преміум-підписки

❓ Якщо у вас виникли питання, натисніть кнопку "Зв'язатися з підтримкою"."""
    await message.answer(help_text)

@router.message(F.text == "⭐ Придбати зірки")
async def stars_menu_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return
    await message.answer(
        "<b>🌟 Оберіть пакет зірок або введіть свою суму:</b>",
        reply_markup=get_stars_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "💎 Придбати Telegram Premium")
async def premium_menu_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return
    await message.answer(
        "<b>💎 Придбати Telegram Premium можна за такими цінами:</b>",
        reply_markup=get_premium_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "💫 Курс зірок")
async def star_rate_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return

    rate_lines = []
    for min_qty, max_qty, price in STAR_PRICE_TIERS:
        rate_lines.append(f"  {min_qty} – {max_qty} зірок → <b>{price}₴</b> за зірку")
    rate_lines.append(f"  {STAR_PRICE_TIERS[-1][1]+1}+ зірок → <b>{STAR_PRICE_DEFAULT}₴</b> за зірку")

    text = (
        f"💫 <b>Актуальний курс зірок:</b>\n\n"
        + "\n".join(rate_lines) +
        f"\n\n<i>Чим більше купуєш — тим вигідніше!</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_star_rate_keyboard())

@router.message(F.text == "👤 Профіль")
async def profile_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return

    user_id = message.from_user.id
    profile = get_user_profile(user_id)

    if not profile:
        save_user(user_id, message.from_user.username, message.from_user.full_name)
        profile = get_user_profile(user_id)

    name = profile.get('full_name') or message.from_user.full_name or "Невідомо"

    profile_text = f"""<b>👤 Інформація про {name}</b>

🆔 ID: <code>{user_id}</code>
⭐ Зірки (куплено всього): <b>{profile['total_stars']}</b>
💰 Всього поповнено: <b>{profile['total_uah']:.2f} грн</b>
💸 Реферальних зірок: <b>{profile['referral_balance']}</b>"""

    await message.answer(profile_text, parse_mode="HTML", reply_markup=get_profile_keyboard())

@router.message(F.text == "💻 Зв'язатися з підтримкою")
async def support_contact_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    random_admin_id = random.choice(ADMIN_IDS)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати підтримці", url=f"tg://user?id={random_admin_id}")]
    ])
    await message.answer("<b>🆘 Для зв'язку з підтримкою натисніть кнопку нижче:</b>",
                         reply_markup=keyboard, parse_mode="HTML")

@router.message(F.text == "📣 Канал з відгуками")
async def reviews_channel_handler(message: types.Message, state: FSMContext):
    await clear_user_state(state, message.from_user.id)
    if not await subscription_required(message, message.bot):
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Перейти до каналу", url="https://t.me/starsZEMSTA")]
    ])
    await message.answer("<b>📣 Перегляньте відгуки наших клієнтів у нашому каналі:</b>",
                         reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data == "show_star_rate")
async def show_star_rate_callback(callback: types.CallbackQuery):
    rate_lines = []
    for min_qty, max_qty, price in STAR_PRICE_TIERS:
        rate_lines.append(f"  {min_qty} – {max_qty} зірок → <b>{price}₴</b> за зірку")
    rate_lines.append(f"  {STAR_PRICE_TIERS[-1][1]+1}+ зірок → <b>{STAR_PRICE_DEFAULT}₴</b> за зірку")

    text = (
        f"💫 <b>Актуальний курс зірок:</b>\n\n"
        + "\n".join(rate_lines) +
        f"\n\n<i>Чим більше купуєш — тим вигідніше!</i>"
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_star_rate_keyboard())
    await callback.answer()

@router.callback_query(F.data == "go_buy_stars")
async def go_buy_stars_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "<b>🌟 Оберіть пакет зірок або введіть свою суму:</b>",
        reply_markup=get_stars_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "top_up_balance")
async def top_up_balance_callback(callback: types.CallbackQuery):
    await callback.message.answer(
        "<b>🌟 Оберіть пакет зірок або введіть свою суму:</b>",
        reply_markup=get_stars_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "show_referral")
async def show_referral_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await callback.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    from database import get_referral_stats
    from keyboards import get_referral_keyboard
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
    from keyboards import get_withdrawal_keyboard
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

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(callback.bot, user_id):
        await callback.message.edit_text("✅ Ви успішно підписалися на канал. Тепер можете користуватися ботом!", reply_markup=None)
        await callback.bot.send_message(user_id, "🌟 Ласкаво просимо! Оберіть дію:", reply_markup=get_main_menu(user_id))
    else:
        await callback.answer("❌ Ви ще не підписалися на канал. Будь ласка, підпішіться та спробуйте знову.")

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await clear_user_state(state, callback.from_user.id)
    await callback.message.answer("🔙 Повернення до головного меню:", reply_markup=get_main_menu(callback.from_user.id))
    await callback.answer()

@router.message(F.text.in_(['відміна', 'отмена', 'cancel', '/cancel', '❌ відміна']))
async def cancel_any_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        data = await state.get_data()
        order_id = data.get('order_id')
        if order_id and order_id in orders:
            del orders[order_id]
        await state.clear()
        await message.answer("❌ Операція скасована.", reply_markup=get_main_menu(message.from_user.id))
    else:
        await message.answer("🏠 Ви в головному меню.", reply_markup=get_main_menu(message.from_user.id))

@router.message(F.text, ~F.text.startswith('/'))
async def handle_other_messages(message: types.Message, state: FSMContext):
    if not await subscription_required(message, message.bot):
        return
    await clear_user_state(state, message.from_user.id)
    await message.answer("❓ Оберіть дію з меню нижче або введіть /help для довідки:", reply_markup=get_main_menu(message.from_user.id))