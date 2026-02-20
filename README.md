# ⭐ Telegram Stars & Premium Bot

A professional Telegram bot for selling **Telegram Stars** and **Telegram Premium** subscriptions with flexible pricing and multiple payment methods. Built with **aiogram 3.x**, SQLite database, and integration with external delivery API.

## Features

### Core Functionality

- **Flexible Star Packages**: Quick presets (13⭐, 21⭐, 26⭐, 50⭐🔥) or custom amount input
- **Premium Subscriptions**: 3, 6, or 12-month packages
- **Dual Payment System**: 
  - Card payments (Ukrainian bank cards, UAH)
  - Cryptocurrency (TON Connect integration)
- **Channel Subscription Gate**: Mandatory subscription verification before purchase
- **Review System**: Automatic posting to public review channel with ratings
- **Admin Panel**: Statistics, broadcasts, order management
- **Smart Pricing**: Unified rate of 0.84 UAH per star

### Advanced Features

- **Custom Star Amount**: Users can enter any quantity (1-100,000 stars)
- **Auto-calculation**: Real-time price calculation based on star quantity
- **Order Confirmation**: Preview before payment with detailed breakdown
- **Manual Admin Approval**: Card payments reviewed by administrators
- **TON Integration**: Direct wallet connection for crypto payments
- **User Database**: SQLite-based user and review storage
- **Order Tracking**: Real-time status updates for all orders

### Smart Management

- **Statistics Dashboard**: Total users, active orders, uptime tracking
- **Broadcast System**: Mass messaging to all bot users
- **Error Recovery**: Auto-restart on critical errors (configurable)
- **Logging**: Comprehensive logging with rotation
- **Session Persistence**: Maintains state across restarts

## Requirements

- Python 3.8+
- Telegram Bot Token
- SQLite (included with Python)
- External delivery API credentials (SPLIT API)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/fedyaqq34356/stars.git
cd stars
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
SPLIT_API_TOKEN=your_split_api_token
SPLIT_API_URL=https://api.split.example.com
REVIEWS_CHANNEL_ID=-1001234567890
MAIN_CHANNEL_ID=-1001234567890
CARD_NUMBER=1234567890123456
RESTART_ON_ERROR=true
DB_PATH=bot_database.db
```

#### Getting Bot Token:

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token to `.env` file

#### Admin IDs:

1. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)
2. Add multiple admin IDs separated by commas
3. Example: `ADMIN_IDS=123456789,987654321,555555555`

#### Channel Setup:

1. Create a public channel for reviews
2. Add your bot as administrator
3. Get channel ID (starts with -100)
4. Set `REVIEWS_CHANNEL_ID` and `MAIN_CHANNEL_ID`

### 2. Pricing Configuration

Edit `config.py` to adjust pricing:
```python
STAR_PRICE_PER_UNIT = 0.84  # Price per star in UAH

STAR_PRICES = {
    "13⭐ – 11₴": {"stars": 13, "price": 10.92, "type": "stars"},
    "21⭐ – 18₴": {"stars": 21, "price": 17.64, "type": "stars"},
    "26⭐ – 22₴": {"stars": 26, "price": 21.84, "type": "stars"},
    "50⭐ – 42₴🔥": {"stars": 50, "price": 42.00, "type": "stars"},
    "3 місяці💎 – 669₴": {"months": 3, "price": 669, "type": "premium"},
    "6 місяців💎 – 999₴": {"months": 6, "price": 999, "type": "premium"},
    "12 місяців💎 – 1699₴": {"months": 12, "price": 1699, "type": "premium"},
}
```

**To change star price:** Simply modify `STAR_PRICE_PER_UNIT` value.

### 3. External API Integration

The bot requires SPLIT API for order fulfillment:

- `SPLIT_API_URL`: Base API endpoint
- `SPLIT_API_TOKEN`: Bearer token for authentication

API endpoints used:
- `/buy/stars` - Star delivery
- `/buy/premium` - Premium subscription activation

## Database Structure

The bot automatically creates an SQLite database with two tables:

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

- Stores all bot users
- Auto-saves on first `/start` command
- Used for broadcasts and statistics

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    rating INTEGER,
    review_text TEXT,
    order_id TEXT,
    created_at TEXT
)
```

- Stores user reviews with 1-5 star ratings
- Links reviews to specific orders
- Auto-increments review IDs from 322
- Published automatically to review channel

## Usage

### Starting the Bot

Run the main script:
```bash
python main.py
```

Console output:
```
🌟 Telegram Bot для продажу зірок та Telegram Premium
🚀 Запуск бота...
👤 Адміністратор: [123456789, 987654321]
🔗 API Split: https://api.example.com
📺 Канал відгуків: -1001234567890
🔄 Авто-перезапуск: ✅
💳 Номер картки: 1234567890123456
💾 База даних: bot_database.db
```

### Bot Commands

#### For Regular Users:

- `/start` - Start the bot and open main menu
- `/help` - View detailed usage instructions

#### For Administrators:

- `/start` - Open admin main menu (includes broadcast button)
- `/stats` - View bot statistics
- `/sendall <message>` - Broadcast to all users
- `/restart` - Restart the bot
- `/migrate_users` - Migrate users to database (maintenance)

## User Flow

### Buying Stars - Quick Packages
```
User: /start
Bot: 🌟 Ласкаво просимо!
     [Image: welcome_image.jpg]
     [Buttons: ⭐ Buy Stars | 💎 Buy Premium | 💻 Support | 📣 Reviews]

User: [⭐ Buy Stars]
Bot: 🌟 Оберіть пакет зірок або введіть свою суму:
     💰 Ціна: 0.84₴ за 1 зірку
     [13⭐ – 11 грн]
     [21⭐ – 18 грн]
     [26⭐ – 22 грн]
     [50⭐ – 42 грн🔥]
     [✏️ Ввести свою суму]

User: [50⭐ – 42 грн🔥]
Bot: 💳 Оберіть спосіб оплати:
     ⭐ Кількість зірок: 50
     💰 Сума до оплати: 42₴
     [💳 Card] [💎 TON]

User: [💳 Card]
Bot: ✨ Вкажіть @username (тег), на який треба відправити зірки.
     ⚠️ Обов'язково перевірте правильність!

User: @myusername
Bot: 💳 Банк України
     Карта: 1234567890123456
     💰 До оплати: 42.00 UAH
     ⚙️ Зірки на аккаунт: @myusername
     ⭐ @myusername отримає: 50 ⭐
     📸 Після оплати надішліть квитанцію

User: [Sends payment screenshot]
Bot: ✅ Скріншот отримано!
     ⏳ Очікуйте підтвердження (зазвичай до 30 хвилин)

[Admin approves payment]

Bot: ✅ Ваша оплата підтверджена!
     💫 Замовлення обробляється.
     ‼️ Це займе від 5 хвилин до 2 годин.
     
     🌟 Залиште відгук про нашу роботу:
     [⭐ Leave Review]
```

### Buying Stars - Custom Amount
```
User: [✏️ Ввести свою суму]
Bot: 🌟 Введіть суму зірок, яку хочете купити:
     💰 Ціна: 0.84₴ за 1 зірку

User: 137
Bot: 📋 Підтвердіть замовлення:
     ⭐ Кількість зірок: 137
     💰 Вартість: 115.08₴
     Підтвердити замовлення?
     [✅ Підтвердити] [❌ Скасувати]

User: [✅ Підтвердити]
Bot: 💳 Оберіть спосіб оплати:
     [💳 Card] [💎 TON]
     [... continues as above ...]
```

### Buying Premium
```
User: [💎 Buy Premium]
Bot: 💎 Придбати Telegram Premium:
     [3 місяці – 669₴] [6 місяців – 999₴]
     [12 місяців – 1699₴]

User: [6 місяців – 999₴]
Bot: 💳 Оберіть спосіб оплати:
     💎 Термін: 6 місяців
     💰 Сума до оплати: 999₴
     [💳 Card] [💎 TON]

[... payment flow same as stars ...]
```

### Leaving a Review
```
Bot: 🌟 Залиште відгук про нашу роботу:
     [⭐ Залишити відгук]

User: [⭐ Залишити відгук]
Bot: ⭐ Оцініть нашу роботу:
     [⭐] [⭐⭐] [⭐⭐⭐] [⭐⭐⭐⭐] [⭐⭐⭐⭐⭐]

User: [⭐⭐⭐⭐⭐]
Bot: Ваша оцінка: ⭐⭐⭐⭐⭐
     💬 Тепер напишіть текст відгуку:

User: Amazing service! Got my stars in 10 minutes!
Bot: ✅ Дякуємо за відгук! Він опубліковано в нашому каналі.

[Posted to review channel]:
⭐ НОВИЙ ВІДГУК #322 ⭐
👤 Користувач: John Doe
📱 Username: @johndoe
🌟 Куплено зірок: 50
🌟 Оцінка: ⭐⭐⭐⭐⭐
📝 Відгук: Amazing service! Got my stars in 10 minutes!
📅 Дата: 2026-02-16 14:30:00
```

## Admin Panel

### Statistics
```
Admin: /stats
Bot: 📊 Статистика бота:
     👥 Загальна кількість користувачів: 1,547
     📋 Активних замовлень: 3
     🕒 Час роботи: 2026-02-16 14:30:00
     📺 Канал відгуків: -1001234567890
     🔄 Авто-перезапуск: ✅
```

### Broadcasting

**Method 1: Command**
```
Admin: /sendall Новий розпродаж! -20% на всі пакети зірок!
Bot: 📡 Розпочинаю розсилку для 1,547 користувачів...
     📊 Розсилка завершена!
     ✅ Успішно: 1,540
     ❌ Помилок: 7
```

**Method 2: Menu**
```
Admin: [📤 Розсилка]
Bot: 📝 Введіть текст для розсилки:

Admin: 🎉 Спеціальна пропозиція тільки сьогодні!
Bot: 📡 Розпочинаю розсилку для 1,547 користувачів...
     [... same as above ...]
```

### Order Approval

When user sends payment screenshot:
```
[Admin receives]:
💳 Новий заказ з оплатою картою:
👤 Користувач: John Doe (ID: 123456789)
📝 Username: @johndoe
📦 Тип: Звезды
⭐ Кількість: 50
💰 Сумма: 42₴
💳 Спосіб оплати: Картой
🕒 Час: 2026-02-16 14:25:00

Скрін оплати:
[Screenshot image]

[✅ Підтвердити] [❌ Відмінити]

Admin: [✅ Підтвердити]
Bot: ✅ Заказ підтверджено!
     [🔗 Перейти в магазин]
```

## Payment Processing

### Card Payment Flow

1. **User Selection**: User chooses card payment method
2. **Username Input**: User provides Telegram @username for delivery
3. **Payment Info**: Bot displays card number and amount
4. **Screenshot Upload**: User uploads payment confirmation
5. **Admin Review**: Order sent to all admins for approval
6. **Approval**: Admin clicks ✅ Підтвердити
7. **Processing**: Order marked as completed
8. **Delivery**: External API delivers stars/premium (5min - 2hrs)
9. **Review Request**: User prompted to leave review

### TON Payment Flow

1. **User Selection**: User chooses TON payment
2. **Admin Pre-approval**: Order sent to admin for approval
3. **API Request**: Bot requests transaction details from SPLIT API
4. **TON Connect**: User receives deeplink to wallet
5. **Transaction**: User confirms in TON wallet
6. **Delivery**: Automatic delivery after blockchain confirmation

### Payment Validation

**Card Payment:**
- Username format: `^[a-zA-Z0-9_]{5,32}$`
- Must not contain spaces, slashes, or quotes
- Screenshot required (photo only)

**TON Payment:**
- Transaction amount matches order price
- Valid recipient address from API
- Payload verification

## Project Structure
```
stars/
├── main.py                      # Entry point, bot initialization
├── config.py                    # Configuration, environment variables
├── database.py                  # SQLite operations
├── api_client.py                # SPLIT API integration
├── states.py                    # FSM state definitions
├── keyboards.py                 # Inline/reply keyboard layouts
├── utils.py                     # Utility functions (subscription check, restart)
│
├── handlers/                    # Request handlers
│   ├── common.py               # /start, /help, main menu
│   ├── orders.py               # Order creation, package selection
│   ├── payments.py             # Payment processing, admin approval
│   ├── reviews.py              # Review collection and posting
│   └── admin.py                # Admin commands, broadcasts
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── LICENSE                      # GPL v3.0
├── README.md                    # This file
│
└── bot_database.db             # SQLite database (auto-generated)
```

## How It Works

### Architecture
```
┌─────────────────────────────────────────────────┐
│                   User Interface                │
│              (Telegram Messages)                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│              Handler Layer                      │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │ Common   │ Orders   │ Payments │ Reviews  │ │
│  │ Handlers │ Handlers │ Handlers │ Handlers │ │
│  └──────────┴──────────┴──────────┴──────────┘ │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Business Logic Layer                 │
│  ┌───────────────┬──────────────┬─────────────┐ │
│  │ Order Manager │ API Client   │ Utils       │ │
│  │               │              │             │ │
│  └───────────────┴──────────────┴─────────────┘ │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│               Data Layer                        │
│  ┌──────────────────┬─────────────────────────┐ │
│  │ SQLite Database  │ External SPLIT API      │ │
│  │ (Users, Reviews) │ (Order Fulfillment)     │ │
│  └──────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Order Lifecycle
```
[Create Order] → [Payment Method Selection] → [Payment Process]
                                                      │
                    ┌─────────────────────────────────┴─────────────────┐
                    ▼                                                   ▼
            [Card Payment]                                      [TON Payment]
                    │                                                   │
            [Username Input]                                   [Admin Approval]
                    │                                                   │
            [Payment Info Display]                              [API Transaction]
                    │                                                   │
            [Screenshot Upload]                                 [TON Connect]
                    │                                                   │
            [Admin Approval]                                    [Auto Delivery]
                    │                                                   │
                    └─────────────────────────────────────┬─────────────┘
                                                          ▼
                                                  [Order Complete]
                                                          │
                                                  [Review Request]
                                                          │
                                                  [Review Published]
```

### State Machine (FSM)
```python
# Order Creation States
StarsOrderStates.waiting_for_stars_amount

# Card Payment States
CardPaymentStates.waiting_for_username
CardPaymentStates.waiting_for_payment_screenshot

# Review States
ReviewStates.waiting_for_rating
ReviewStates.waiting_for_review

# Admin States
BroadcastStates.waiting_for_broadcast_text
```

## API Integration

### SPLIT API Endpoints

#### Get Recipient Address
```python
POST /buy/stars
POST /buy/premium

Headers:
  Authorization: Bearer {SPLIT_API_TOKEN}
  Content-Type: application/json

Body (Stars):
{
  "user_id": 123456789,
  "username": "johndoe",
  "quantity": 50
}

Body (Premium):
{
  "user_id": 123456789,
  "username": "johndoe",
  "months": 6
}

Response:
{
  "message": {
    "transaction": {
      "messages": [
        {
          "address": "UQBx...",
          "amount": "1000000",
          "payload": "base64_encoded_data"
        }
      ]
    }
  }
}
```

### Error Handling
```python
# Connection errors
try:
    response = await get_recipient_address(...)
except aiohttp.ClientError as e:
    logger.error(f"API connection error: {e}")
    await message.answer("❌ Помилка зв'язку з сервером")

# Invalid responses
if not response or response.status != 200:
    logger.error(f"API error: {response.status}")
    await message.answer("❌ Помилка обробки замовлення")

# Missing data
if not address:
    logger.error("Address missing in API response")
    await message.answer("❌ Помилка отримання адреси")
```

## Logging

Logs are written to console with detailed formatting:
```
2026-02-16 14:30:00 - __main__ - INFO - Бот запущен
2026-02-16 14:30:15 - handlers.common - INFO - Пользователь 123456789 запустил бот
2026-02-16 14:30:45 - handlers.orders - INFO - Пользователь 123456789 выбрал пакет: 50⭐ – 42₴🔥
2026-02-16 14:31:20 - handlers.payments - INFO - Заказ stars_123456789_1708088480 отправлен администратору
2026-02-16 14:32:00 - handlers.reviews - INFO - Пользователь 123456789 начал процесс оставления отзыва
```

### Log Levels

- **INFO**: Normal operations, user actions
- **WARNING**: Non-critical issues, subscription failures
- **ERROR**: Errors, exceptions, API failures
- **CRITICAL**: Fatal errors triggering restarts

## Troubleshooting

### Common Issues

#### Issue: "❌ Бот не є адміністратором каналу"

**Solution:**
1. Add bot to your channel
2. Promote to administrator
3. Grant "Post messages" permission
4. Restart bot

#### Issue: "❌ Помилка: дані замовлення не знайдено"

**Solution:**
1. Don't close the bot during order creation
2. Complete each step without canceling
3. If stuck, send `/cancel` and start over

#### Issue: Payment screenshot not uploading

**Solution:**
1. Send only photos (not documents)
2. Don't compress images
3. Ensure file size < 10MB
4. Try different image format (JPG, PNG)

#### Issue: TON payment not working

**Solution:**
1. Verify SPLIT API credentials in `.env`
2. Check API URL is correct
3. Ensure admin approved the order first
4. Check logs for API errors

#### Issue: Reviews not posting to channel

**Solution:**
1. Verify `REVIEWS_CHANNEL_ID` is correct
2. Ensure bot is admin in review channel
3. Check bot has "Post messages" permission
4. Test by sending message manually

#### Issue: Users can't access bot after subscription

**Solution:**
1. Verify `MAIN_CHANNEL_ID` is set correctly
2. Bot must be admin in subscription channel
3. User must actually click subscribe
4. Try removing and re-adding user to channel

#### Issue: Database locked error

**Solution:**
1. Stop all bot instances (only run one)
2. Close any SQLite database browsers
3. Delete `bot_database.db` if corrupted (loses data!)
4. Restart bot to recreate database

### Debug Mode

Enable detailed logging in `main.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks

**Test subscription system:**
```bash
# Check if bot can see channel
# Bot must be admin with "View channel" permission
```

**Test API connection:**
```python
from api_client import check_split_api_health
result = await check_split_api_health()
print(f"API Status: {'✅' if result else '❌'}")
```

**Test database:**
```python
from database import get_users_count
count = get_users_count()
print(f"Total users: {count}")
```

## Security Considerations

### Environment Variables

**Never commit `.env` to Git:**
```bash
# .gitignore already includes:
.env
bot_database.db
*.session
__pycache__/
```

### Admin Access

- Admin IDs verified on every admin command
- No privilege escalation possible
- Commands logged for audit trail

### User Data

- User IDs stored, not phone numbers
- Usernames public (visible in reviews)
- Payment screenshots sent only to admins
- No credit card data stored

### Payment Security

- Bot never stores payment details
- Screenshot verification by human admins
- External API handles actual transactions
- Order IDs prevent replay attacks

### API Security

- Bearer token authentication
- HTTPS only connections
- Rate limiting handled by external API
- Timeout protection (30s max)

## Performance

### Specifications

- **Database**: SQLite (suitable for <100K users)
- **Memory**: ~30-50MB typical usage
- **Concurrent Users**: Handles multiple simultaneous orders
- **Response Time**: <500ms for most operations
- **Broadcast Speed**: ~50 messages/second (with delays)

### Optimization Tips

#### For Large User Base (10K+ users):
```python
# Increase broadcast delay to avoid flood
await asyncio.sleep(0.05)  # 50ms between messages
```

#### For High Order Volume:
```python
# Consider moving to PostgreSQL
# Add connection pooling
# Implement caching for user lookups
```

#### For Better Reliability:

- Deploy on VPS (not local computer)
- Use process manager (systemd, supervisor)
- Enable auto-restart on crash
- Monitor logs regularly

### Database Maintenance
```python
# Clean old completed orders (manual)
DELETE FROM reviews WHERE created_at < date('now', '-90 days');

# Vacuum database (optimize)
VACUUM;

# Backup database
cp bot_database.db bot_database_backup_$(date +%Y%m%d).db
```

## Deployment

### VPS Deployment (Recommended)
```bash
# 1. Connect to VPS
ssh user@your-vps-ip

# 2. Clone repository
git clone https://github.com/fedyaqq34356/stars.git
cd stars

# 3. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure
nano .env  # Add your credentials

# 5. Test run
python main.py

# 6. Setup systemd service
sudo nano /etc/systemd/system/stars-bot.service
```

**systemd service file:**
```ini
[Unit]
Description=Telegram Stars Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/stars
Environment=PATH=/home/yourusername/stars/venv/bin
ExecStart=/home/yourusername/stars/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable stars-bot
sudo systemctl start stars-bot
sudo systemctl status stars-bot
```

### Docker Deployment (Alternative)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```
```bash
docker build -t stars-bot .
docker run -d --name stars-bot --env-file .env stars-bot
```

## Dependencies
```
aiogram==3.15.0      # Modern Telegram Bot framework
aiohttp==3.10.11     # Async HTTP client
python-dotenv==1.0.1 # Environment variable management
asyncio==3.4.3       # Async I/O support
```

### Dependency Updates
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade aiogram

# Update all
pip install --upgrade -r requirements.txt
```

## Contributing

We welcome contributions! Here's how:

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/stars.git
cd stars
```

### 2. Create Feature Branch
```bash
git checkout -b feature/amazing-feature
```

### 3. Make Changes

- Follow existing code style
- Add comments for complex logic
- Update README if needed
- Test thoroughly

### 4. Commit Changes
```bash
git add .
git commit -m "Add amazing feature"
```

### 5. Push and Create PR
```bash
git push origin feature/amazing-feature
```

Then create Pull Request on GitHub.

### Code Style Guidelines

- Use type hints where possible
- Follow PEP 8 conventions
- Keep functions under 50 lines
- Add docstrings for complex functions
- Use meaningful variable names

## Support

### Get Help

- **GitHub Issues**: [https://github.com/fedyaqq34356/stars/issues](https://github.com/fedyaqq34356/stars/issues)
- **Repository**: [https://github.com/fedyaqq34356/stars](https://github.com/fedyaqq34356/stars)

### Reporting Bugs

Include:
1. Bot version
2. Python version
3. Error message (from logs)
4. Steps to reproduce
5. Expected vs actual behavior

### Feature Requests

Open an issue with:
1. Clear description of feature
2. Use case / motivation
3. Suggested implementation (optional)

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

See [LICENSE](LICENSE) file for full text.

### What this means:

- ✅ Free to use commercially
- ✅ Can modify the code
- ✅ Can distribute copies
- ⚠️ Must disclose source
- ⚠️ Must use same license
- ⚠️ Must state changes

## Acknowledgments

- **aiogram** - Excellent async Telegram Bot framework
- **Telegram** - For the Bot API
- **SPLIT** - Delivery API integration
- **Community** - Bug reports and feature suggestions

## Roadmap

### Planned Features

- [ ] Multiple currency support
- [ ] Automated delivery status tracking
- [ ] Receipt generation (PDF)
- [ ] Referral system
- [ ] Promo code system
- [ ] Analytics dashboard
- [ ] Multi-language support

### Under Consideration

- [ ] Web dashboard for admins
- [ ] Automated refund system
- [ ] Integration with more payment providers
- [ ] Mobile app companion

## Changelog

### Version 2.0.0 (2026-02-16)

**Added:**
- Custom star amount input
- Unified pricing (0.84 UAH/star)
- Quick package presets (13, 21, 26, 50)
- Order confirmation before payment
- Hot deal indicator (🔥) for 50-star package

**Changed:**
- Removed pagination from star selection
- Simplified pricing configuration
- Improved order flow UX

**Fixed:**
- Database auto-increment starting from 322
- Username validation regex
- Screenshot upload handling

### Version 1.0.0 (Initial Release)

- Basic star packages
- Premium subscriptions
- Card and TON payments
- Review system
- Admin panel

---

Made with ❤️ for the Telegram community

⭐ **Star this repo** if you find it useful!