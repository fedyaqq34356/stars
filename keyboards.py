from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from typing import Dict
from config import ADMIN_IDS

def get_main_menu(user_id: int = None) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="⭐ Придбати зірки"), KeyboardButton(text="💎 Придбати Telegram Premium")],
        [KeyboardButton(text="👤 Профіль"), KeyboardButton(text="💫 Курс зірок")],
        [KeyboardButton(text="💻 Зв'язатися з підтримкою"), KeyboardButton(text="📣 Канал з відгуками")],
    ]
    if user_id is not None and user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="📤 Розсилка")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_stars_menu():
    buttons = [
        [InlineKeyboardButton(text="13⭐ – 20 грн", callback_data="select_13⭐ – 20₴")],
        [InlineKeyboardButton(text="21⭐ – 30 грн", callback_data="select_21⭐ – 30₴")],
        [InlineKeyboardButton(text="26⭐ – 40 грн", callback_data="select_26⭐ – 40₴")],
        [InlineKeyboardButton(text="50⭐ – 46 грн 🔥", callback_data="select_50⭐ – 46₴")],
        [InlineKeyboardButton(text="✏️ Ввести свою суму", callback_data="custom_stars_amount")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_menu():
    buttons = [
        [InlineKeyboardButton(text="3 місяці💎 – 669₴", callback_data="select_3 місяці💎 – 669₴"),
         InlineKeyboardButton(text="6 місяців💎 – 999₴", callback_data="select_6 місяців💎 – 999₴")],
        [InlineKeyboardButton(text="12 місяців💎 – 1699₴", callback_data="select_12 місяців💎 – 1699₴")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_order_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_stars_order")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_stars_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_method_keyboard(order_id: str):
    buttons = [
        [InlineKeyboardButton(text="💳 Сплатити карткою", callback_data=f"pay_card_{order_id}")],
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_card_approval_keyboard(order_id: str):
    buttons = [
        [InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"approve_{order_id}"),
         InlineKeyboardButton(text="❌ Відмінити", callback_data=f"reject_{order_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_review_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐ Залишити відгук", callback_data="leave_review")],
        [InlineKeyboardButton(text="Пропустити", callback_data="skip_review")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_withdrawal_review_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐ Залишити відгук про вивід", callback_data="leave_withdrawal_review")],
        [InlineKeyboardButton(text="Пропустити", callback_data="skip_review")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_rating_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐", callback_data="rate_1")],
        [InlineKeyboardButton(text="⭐⭐", callback_data="rate_2")],
        [InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subscription_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📺 Підписатися", url="https://t.me/starsZEMSTA_news")],
        [InlineKeyboardButton(text="✅ Перевірити підписку", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_username_input_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_payment_method")],
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_screenshot_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_username_input")],
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_referral_keyboard(referral_link: str, bot_username: str = None):
    promo_text = "⭐️ Купуй зірки Telegram дешевше — економія 20-30%!"
    import urllib.parse
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(referral_link)}&text={urllib.parse.quote(promo_text)}"
    buttons = [
        [InlineKeyboardButton(text="👥 Запросити друга", url=share_url)],
        [InlineKeyboardButton(text="💸 Вивести зірки", callback_data="show_withdrawal")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_withdrawal_keyboard():
    buttons = [
        [InlineKeyboardButton(text="💸 Вивід", callback_data="start_withdrawal")],
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_withdrawal")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔗 Реферальна система", callback_data="show_referral")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_star_rate_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐ Придбати зірки", callback_data="go_buy_stars")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)