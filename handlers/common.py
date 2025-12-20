import logging
import random
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import save_user, load_users
from keyboards import get_main_menu, get_stars_menu, get_premium_menu, get_subscription_keyboard
from utils import check_subscription
from config import ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()
user_ids = load_users()

async def subscription_required(message, bot) -> bool:
    if not await check_subscription(bot, message.from_user.id):
        subscription_text = """❌ Щоб користуватися ботом, потрібно підписатися на наш основний канал!

📺 Підпишіться на канал і натисніть кнопку "Перевірити підписку" """
        
        await bot.send_message(
            message.from_user.id,
            subscription_text,
            reply_markup=get_subscription_keyboard()
        )
        logger.info(f"Пользователь {message.from_user.id} не подписан")
        return False
    return True

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_ids.add(user_id)
    save_user(user_id)
    
    if not await subscription_required(message, message.bot):
        return
    
    welcome_text = """<b>🌟 Ласкаво просимо до @ZEMSTA_stars_bot!❄️</b>
<b>✨ Обирай, купуй і користуйся зірками!</b>

<b>🎁🔥 Економія до 30%!</b>

<b>💎☃️ Оплата TON або ₴ — як зручно.</b>

<b>👇 Натисни кнопки нижче і починай легко! 😊</b>"""
    
    try:
        photo = types.FSInputFile('welcome_image.jpg')
        await message.answer_photo(photo, caption=welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")
    except FileNotFoundError:
        logger.warning("Файл welcome_image.jpg не найден")
        await message.answer(welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await message.answer(welcome_text, reply_markup=get_main_menu(user_id), parse_mode="HTML")
    
    logger.info(f"Пользователь {message.from_user.id} запустил бот")

@router.message(Command("help"))
async def help_command(message: types.Message):
    help_text = """📋 Як купити зірки або Telegram Premium:

1️⃣ Оберіть "Придбати зірки" або "Придбати Telegram Premium" у меню
2️⃣ Виберіть потрібний пакет
3️⃣ Оберіть спосіб оплати (TON или картой)
4️⃣ Очікуйте підтвердження адміністратора
5️⃣ Для оплати TON: підтвердіть транзакцію в гаманці.
Для оплати карткою: надішліть username, а потім скриншот оплати.
6️⃣ Очікуйте автоматичного зарахування зірок или преміум-підписки

❓ Якщо у вас виникли питання, натисніть кнопку "Зв'язатися з підтримкою"."""    
    await message.answer(help_text)
    logger.info(f"Пользователь {message.from_user.id} запросил справку")

@router.message(F.text == "⭐ Придбати зірки")
async def stars_menu_handler(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил меню звезд")
    if not await subscription_required(message, message.bot):
        logger.warning(f"Пользователь {message.from_user.id} не подписан на канал")
        return
        
    await message.answer(
        "<b>🌟🎅 Придбати зірки можна за такими цінами:</b>",
        reply_markup=get_stars_menu(page=1),
        parse_mode="HTML"
    )

@router.message(F.text == "💎 Придбати Telegram Premium")
async def premium_menu_handler(message: types.Message):
    if not await subscription_required(message, message.bot):
        return
        
    await message.answer(
        "<b>💎🎄 Придбати Telegram Premium можна за такими цінами:</b>",
        reply_markup=get_premium_menu(),
        parse_mode="HTML"
    )

@router.message(F.text == "📣 Канал з відгуками")
async def reviews_channel_handler(message: types.Message):
    if not await subscription_required(message, message.bot):
        return
        
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣🎅 Перейти до каналу", url="https://t.me/starsZEMSTA")]
    ])
    
    await message.answer(
        "<b>📣 Перегляньте відгуки наших клієнтів у нашому каналі:</b>", 
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {message.from_user.id} запросил канал с отзывами")

@router.message(F.text == "💻 Зв'язатися з підтримкою")
async def support_contact_handler(message: types.Message):
    if not await subscription_required(message, message.bot):
        return
        
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    random_admin_id = random.choice(ADMIN_IDS)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬❄️ Написати підтримці", url=f"tg://user?id={random_admin_id}")]
    ])
    
    await message.answer(
        "<b>🆘☃️ Для зв'язку з підтримкою натисніть кнопку нижче:</b>", 
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    logger.info(f"Користувач {message.from_user.id} запросив підтримку")

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    if await check_subscription(callback.bot, user_id):
        await callback.message.edit_text(
            "✅ Ви успішно підписалися на канал. Тепер можете користуватися ботом!",
            reply_markup=None
        )
        await callback.bot.send_message(user_id, "🌟☃️Ласкаво просимо! Оберіть дію:", reply_markup=get_main_menu(user_id))
        logger.info(f"Пользователь {user_id} прошел проверку подписки")
    else:
        await callback.answer("❌ Ви ще не підписалися на канал. Будь ласка, підпишіться та спробуйте знову.")
        logger.warning(f"Пользователь {user_id} не подписан на канал")

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        "🔙 Повернення до головного меню:",
        reply_markup=get_main_menu(callback.from_user.id)
    )
    await callback.answer()
    logger.info(f"Пользователь {callback.from_user.id} вернулся в главное меню")

@router.message(F.text.in_(['відміна', 'отмена', 'cancel', '/cancel', '❌ відміна']))
async def cancel_any_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        data = await state.get_data()
        order_id = data.get('order_id')
        
        from utils import orders
        if order_id and order_id in orders:
            del orders[order_id]
            
        await state.clear()
        await message.answer("❌ Операція скасована.", reply_markup=get_main_menu(message.from_user.id))
        logger.info(f"Пользователь {message.from_user.id} отменил состояние {current_state}")
    else:
        await message.answer("🏠 Ви в головному меню.", reply_markup=get_main_menu(message.from_user.id))

@router.message(F.text, ~F.text.startswith('/'))
async def handle_other_messages(message: types.Message):
    if not await subscription_required(message, message.bot):
        return
        
    await message.answer("❓ Оберіть дію з меню нижче або введіть /help для довідки:", reply_markup=get_main_menu(message.from_user.id))
    logger.info(f"Пользователь {message.from_user.id} отправил неизвестное сообщение")