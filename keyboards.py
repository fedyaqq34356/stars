from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict
from config import ADMIN_IDS

def get_main_menu(user_id: int = None) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="⭐ Придбати зірки")],
        [KeyboardButton(text="💎 Придбати Telegram Premium")],
        [KeyboardButton(text="💻 Зв'язатися з підтримкою")],
        [KeyboardButton(text="📣 Канал з відгуками")]
    ]
    
    if user_id is not None and user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="📤 Розсилка")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_stars_menu(page: int = 1):
    if page == 1:
        buttons = [
            [InlineKeyboardButton(text="50⭐🔥 – 48₴", callback_data="select_50⭐🔥 – 48₴")],
            [InlineKeyboardButton(text="60⭐ – 59₴", callback_data="select_60⭐ – 59₴")],
            [InlineKeyboardButton(text="70⭐ – 69₴", callback_data="select_70⭐ – 69₴")],
            [InlineKeyboardButton(text="80⭐ – 79₴", callback_data="select_80⭐ – 79₴")],
            [InlineKeyboardButton(text="90⭐ – 89₴", callback_data="select_90⭐ – 89₴")],
            [InlineKeyboardButton(text="100⭐🔥 – 85₴", callback_data="select_100⭐🔥 – 85₴")],
            [InlineKeyboardButton(text="⬇️ Більше варіантів", callback_data="stars_page_2")]
        ]
    else:  
        buttons = [
            [InlineKeyboardButton(text="⬆️ Назад", callback_data="stars_page_1")],
            [InlineKeyboardButton(text="200⭐ – 160₴", callback_data="select_200⭐ – 160₴")],
            [InlineKeyboardButton(text="300⭐ – 235₴", callback_data="select_300⭐ – 235₴")],
            [InlineKeyboardButton(text="400⭐ – 310₴", callback_data="select_400⭐ – 310₴")],
            [InlineKeyboardButton(text="500⭐ – 370₴", callback_data="select_500⭐ – 370₴")],
            [InlineKeyboardButton(text="1000⭐ – 735₴", callback_data="select_1000⭐ – 735₴")],
            [InlineKeyboardButton(text="10000⭐ – 7300₴", callback_data="select_10000⭐ – 7300₴")]
        ]
    

    buttons.append([InlineKeyboardButton(text="⬅️ Головне меню", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_menu():
    buttons = [
        [InlineKeyboardButton(text="3 місяці💎 – 669₴", callback_data="select_3 місяці💎 – 669₴"),
         InlineKeyboardButton(text="6 місяців💎 – 999₴", callback_data="select_6 місяців💎 – 999₴")],
        [InlineKeyboardButton(text="12 місяців💎 – 1699₴", callback_data="select_12 місяців💎 – 1699₴")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_method_keyboard(order_id: str):
    buttons = [
        [InlineKeyboardButton(text="💳 Сплатити карткою", callback_data=f"pay_card_{order_id}")],
        [InlineKeyboardButton(text="💎 Сплатити TON", callback_data=f"pay_ton_{order_id}")],
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
        [InlineKeyboardButton(text="⭐ Залишити відгук", callback_data="leave_review")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_rating_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐", callback_data="rate_1"),
         InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
         InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
         InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
         InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subscription_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📺 Підписатися", url="https://t.me/starsZEMSTA_news")],
        [InlineKeyboardButton(text="✅ Перевірити підписку", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_ton_connect_keyboard(transaction_data: Dict, recipient_address: str):
    ton_connect_url = f"ton://transfer/{recipient_address}"
    params = []
    if transaction_data.get('messages'):
        message = transaction_data.get('messages', [{}])[0]
        if message.get('amount'):
            params.append(f"amount={message['amount']}")
        if message.get('payload'):
            params.append(f"bin={message['payload']}")
    if params:
        ton_connect_url += "?" + "&".join(params)
    
    buttons = [
        [InlineKeyboardButton(text="💎 Оплатить через TON Connect", url=ton_connect_url)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="❌ Відміна", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)