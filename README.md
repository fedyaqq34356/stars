# Telegram Stars & Premium Bot

A professional Telegram bot for selling **Telegram Stars** and **Telegram Premium** subscriptions with flexible pricing and multiple payment methods. Built with **aiogram 3.x**, SQLite database, and integration with external delivery API.

## Features

### Core Functionality

- **Flexible Star Packages**: Quick presets (13, 21, 26, 50 stars) or custom amount input
- **Premium Subscriptions**: 3, 6, or 12-month packages
- **Dual Payment System**:
  - Card payments (Ukrainian bank cards, UAH)
  - Cryptocurrency (TON Connect integration)
- **Channel Subscription Gate**: Mandatory subscription verification before purchase
- **Review System**: Automatic posting to public review channel with ratings (numbered from #603)
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

### Profile System

Each user has a profile accessible via the **Profile** button showing:
- User ID
- Total stars purchased (all time)
- Total UAH deposited (all time)
- Referral star balance (stars earned from referrals)
- Quick **Top Up** inline button to start a new purchase

### Referral System

- Every user gets a unique referral link: `https://t.me/BOT_USERNAME?start=ref_USER_ID`
- When a referred user makes a purchase, the referrer earns **1% of the stars bought**
- Referral earnings accumulate as a balance visible in the profile
- Referrer receives a real-time notification for each referral purchase with details
- Accessible via the **Referral System** button in the main menu

### Withdrawal System

- Users can withdraw accumulated referral stars via the **Withdraw Stars** button
- Bot validates the requested amount against the available balance
- Withdrawal request is forwarded to admins for manual processing
- After submitting a withdrawal, user is prompted to leave a withdrawal-specific review

### Automatic Review System

- After admin confirms an order, a 1-hour countdown starts
- If the user does not leave a review within 1 hour, the bot automatically posts to the review channel indicating the buyer chose to remain silent (no rating assigned)
- Manually leaving a review cancels the auto-review timer immediately

### Review Format

Reviews are posted to the channel using a sequential ID starting from **#603**. Usernames are **not displayed** to protect privacy — buyers are identified only by their review number:

```
⭐ НОВИЙ ВІДГУК #603 ⭐

Покупець #603
🌟 Куплено зірок: 200
🌟 Оцінка: ⭐⭐⭐⭐⭐
📝 Відгук: Top

📅 Дата: 2026-02-19 20:49:40

#відгук #зірки #телеграм
```

Withdrawal reviews are labeled `ВІДГУК ПРО ВИВІД`. Silent auto-reviews are posted as `Покупець #N вирішив промовчати` with no rating.

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
    "50⭐ – 42₴": {"stars": 50, "price": 42.00, "type": "stars"},
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
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    username TEXT,
    full_name TEXT,
    total_stars INTEGER DEFAULT 0,
    total_uah REAL DEFAULT 0,
    referral_balance INTEGER DEFAULT 0,
    referred_by INTEGER
)
```

- Stores all bot users with profile stats
- Auto-saves on first `/start` command
- Used for broadcasts and statistics
- `total_stars` and `total_uah` updated on each confirmed purchase
- `referral_balance` accumulates 1% of referral purchases
- `referred_by` links user to their referrer

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    rating INTEGER,
    review_text TEXT,
    order_id TEXT,
    created_at TEXT,
    review_type TEXT DEFAULT 'purchase'
)
```

- Stores user reviews with 1-5 star ratings
- Links reviews to specific orders
- Auto-increments review IDs starting from **603**
- `review_type`: `purchase`, `withdrawal`, or `silent`
- Published automatically to review channel

## Usage

### Starting the Bot

Run the main script:
```bash
python main.py
```

Console output:
```
Telegram Bot for Stars & Telegram Premium
Starting bot...
Admins: [123456789, 987654321]
Split API: https://api.example.com
Reviews channel: -1001234567890
Auto-restart: ON
Card: 1234567890123456
DB: bot_database.db
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
Bot: Welcome to @ZEMSTA_stars_bot!
     [Image: welcome_image.jpg]
     [Buttons: Buy Stars | Buy Premium | Profile | Referral | Withdraw | Support | Reviews]

User: [Buy Stars]
Bot: Choose a star package or enter your amount:
     Price: 0.84 UAH per star
     [13 stars – 11 UAH]
     [21 stars – 18 UAH]
     [26 stars – 22 UAH]
     [50 stars – 42 UAH]
     [Enter custom amount]

User: [50 stars – 42 UAH]
Bot: Choose payment method:
     Stars: 50
     Amount: 42 UAH
     [Pay by Card] [Pay TON]

User: [Pay by Card]
Bot: Enter the @username to send stars to.
     Make sure to check it carefully!

User: @myusername
Bot: Ukrainian Bank
     Card: 1234567890123456
     Amount: 42.00 UAH
     Account: @myusername
     @myusername will receive: 50 stars
     After payment, send the receipt screenshot here

User: [Sends payment screenshot]
Bot: Screenshot received! Your order has been sent to admin.
     Wait for confirmation (usually up to 30 minutes).

[Admin approves payment]

Bot: Your payment is confirmed!
     Order is being processed.
     This will take from 5 minutes to 2 hours.

     Thank you for your purchase! Please leave a review:
     [Leave Review] [Skip]
```

### Buying Stars - Custom Amount
```
User: [Enter custom amount]
Bot: Enter the number of stars you want to buy:
     Price: 0.84 UAH per star

User: 137
Bot: Confirm order:
     Stars: 137
     Price: 115.08 UAH
     Confirm order?
     [Confirm] [Cancel]

User: [Confirm]
Bot: Choose payment method:
     [Pay by Card] [Pay TON]
     [... continues as above ...]
```

### Buying Premium
```
User: [Buy Telegram Premium]
Bot: Buy Telegram Premium:
     [3 months – 669 UAH] [6 months – 999 UAH]
     [12 months – 1699 UAH]

User: [6 months – 999 UAH]
Bot: Choose payment method:
     Duration: 6 months
     Amount: 999 UAH
     [Pay by Card] [Pay TON]

[... payment flow same as stars ...]
```

### Profile
```
User: [Profile button]
Bot: Info about John

     ID: 123456789
     Stars (total purchased): 500
     Total deposited: 420.00 UAH
     Referral stars: 15

     [Top Up Balance]
```

### Referral System
```
User: [Referral System button]
Bot: Hi John! Here is your referral link:

     https://t.me/ZEMSTA_stars_bot?start=ref_123456789

     Friends invited: 3
     Stars bought by referrals: 1500
     Your referral balance: 15 stars

     For each referral purchase you earn 1% of their stars bought.
     [Copy link]
```

### Withdrawal
```
User: [Withdraw Stars button]
Bot: Withdraw Referral Stars

     Referrals: 3
     Stars bought by referrals: 1500
     Available to withdraw: 15 stars

     [Withdrawal] [Cancel]

User: [Withdrawal]
Bot: Enter the number of stars to withdraw (available: 15):

User: 10
Bot: Withdrawal request for 10 stars sent to admin!
     Please wait for processing.
     [Leave withdrawal review] [Skip]
```

### Leaving a Review
```
Bot: Thank you for your purchase! Please leave a review:
     [Leave Review] [Skip]

User: [Leave Review]
Bot: Rate our service:
     [1 star] [2 stars] [3 stars] [4 stars] [5 stars]

User: [5 stars]
Bot: Your rating: 5 stars
     Now write your review text:

User: Amazing service! Got my stars in 10 minutes!
Bot: Thank you for your review! It has been published in our channel.

[Posted to review channel]:
⭐ НОВИЙ ВІДГУК #603 ⭐

Покупець #603
🌟 Куплено зірок: 50
🌟 Оцінка: ⭐⭐⭐⭐⭐
📝 Відгук: Amazing service! Got my stars in 10 minutes!

📅 Дата: 2026-02-16 14:30:00

#відгук #зірки #телеграм
```

### Auto Review (user did not review within 1 hour)
```
[Posted automatically to review channel]:
⭐ НОВИЙ ВІДГУК #604 ⭐

Покупець #604 вирішив промовчати
🌟 Куплено зірок: 50

📅 Дата: 2026-02-20 15:30:00

#відгук #зірки #телеграм
```

## Admin Panel

### Statistics
```
Admin: /stats
Bot: Bot Statistics:
     Total users: 1,547
     Active orders: 3
     Uptime: 2026-02-16 14:30:00
     Reviews channel: -1001234567890
     Auto-restart: ON
```

### Broadcasting

**Method 1: Command**
```
Admin: /sendall New sale! -20% on all star packages!
Bot: Starting broadcast for 1,547 users...
     Broadcast complete!
     Success: 1,540
     Errors: 7
```

**Method 2: Menu**
```
Admin: [Broadcast button]
Bot: Enter text for broadcast:

Admin: Special offer today only!
Bot: Starting broadcast for 1,547 users...
     [... same as above ...]
```

### Order Approval

When user sends payment screenshot:
```
[Admin receives]:
New card payment order:
User: John Doe (ID: 123456789)
Type: Stars
Stars: 50
Amount: 42 UAH
Payment method: Card
Time: 2026-02-16 14:25:00

[Screenshot image]

[Confirm] [Reject]

Admin: [Confirm]
Bot: Payment confirmed!
     [Go to store]
```

### Withdrawal Request

When user submits a withdrawal:
```
[Admin receives]:
Withdrawal request!

User: @johndoe (ID: 123456789)
Amount: 10 stars
```

## Payment Processing

### Card Payment Flow

1. **User Selection**: User chooses card payment method
2. **Username Input**: User provides Telegram @username for delivery
3. **Payment Info**: Bot displays card number and amount
4. **Screenshot Upload**: User uploads payment confirmation
5. **Admin Review**: Order sent to all admins for approval
6. **Approval**: Admin clicks Confirm
7. **Processing**: Order marked as completed, user stats updated
8. **Referral Bonus**: If buyer was referred, referrer gets 1% stars credited instantly
9. **Delivery**: External API delivers stars/premium (5min - 2hrs)
10. **Review Request**: User prompted to leave review, 1-hour auto-review timer starts

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
│   ├── common.py               # /start, /help, main menu, profile view
│   ├── orders.py               # Order creation, package selection
│   ├── payments.py             # Payment processing, admin approval, referral bonus
│   ├── reviews.py              # Review collection, auto-review scheduler
│   ├── profile.py              # Referral system, withdrawal flow
│   └── admin.py                # Admin commands, broadcasts
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── .gitignore                   # Git ignore rules
├── LICENSE                      # GPL v3.0
├── README.md                    # This file
│
└── bot_database.db              # SQLite database (auto-generated)
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
│  ┌────────┬────────┬────────┬────────┬───────┐  │
│  │ Common │ Orders │Payments│Reviews │Profile│  │
│  └────────┴────────┴────────┴────────┴───────┘  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            Business Logic Layer                 │
│  ┌───────────────┬──────────────┬─────────────┐ │
│  │ Order Manager │ API Client   │ Utils       │ │
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
                                          ┌───────────────┴───────────────┐
                                          ▼                               ▼
                                  [Update User Stats]         [Referral Bonus (1%)]
                                          │                               │
                                          └───────────────┬───────────────┘
                                                          ▼
                                                  [Review Request]
                                                          │
                                          ┌───────────────┴───────────────┐
                                          ▼                               ▼
                                  [User Leaves Review]       [1hr Auto-Review Timer]
                                          │                               │
                                  [Review Published]         [Auto Post "Silent"]
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

# Withdrawal States
WithdrawalStates.waiting_for_amount
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
    await message.answer("Connection error")

# Invalid responses
if not response or response.status != 200:
    logger.error(f"API error: {response.status}")
    await message.answer("Order processing error")

# Missing data
if not address:
    logger.error("Address missing in API response")
    await message.answer("Address retrieval error")
```

## Logging

Logs are written to console with detailed formatting:
```
2026-02-16 14:30:00 - __main__ - INFO - Bot started
2026-02-16 14:30:15 - handlers.common - INFO - User 123456789 started bot
2026-02-16 14:30:45 - handlers.orders - INFO - User 123456789 selected package: 50 stars
2026-02-16 14:31:20 - handlers.payments - INFO - Order stars_123456789_1708088480 sent to admin
2026-02-16 14:32:00 - handlers.reviews - INFO - User 123456789 started review process
2026-02-16 14:33:00 - handlers.reviews - INFO - Auto-review scheduled for user 123456789
```

### Log Levels

- **INFO**: Normal operations, user actions
- **WARNING**: Non-critical issues, subscription failures
- **ERROR**: Errors, exceptions, API failures
- **CRITICAL**: Fatal errors triggering restarts

## Troubleshooting

### Common Issues

#### Issue: "Bot is not a channel administrator"

**Solution:**
1. Add bot to your channel
2. Promote to administrator
3. Grant "Post messages" permission
4. Restart bot

#### Issue: "Order data not found"

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

#### Issue: Referral bonus not credited

**Solution:**
1. Ensure the referred user started the bot with the referral link (`?start=ref_ID`)
2. The referrer must exist in the database
3. Check logs for `process_referral_bonus` errors

#### Issue: Auto-review not posting after 1 hour

**Solution:**
1. Bot must stay running continuously (no restarts during the hour)
2. Verify `REVIEWS_CHANNEL_ID` is correct
3. Check logs for `schedule_auto_review` errors

### Debug Mode

Enable detailed logging in `main.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks

**Test API connection:**
```python
from api_client import check_split_api_health
result = await check_split_api_health()
print(f"API Status: {'OK' if result else 'FAIL'}")
```

**Test database:**
```python
from database import get_users_count
count = get_users_count()
print(f"Total users: {count}")
```

**Test referral system:**
```python
from database import get_user_profile, get_referral_stats
profile = get_user_profile(USER_ID)
stats = get_referral_stats(USER_ID)
print(profile, stats)
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
- Usernames NOT shown in public reviews (privacy protection)
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
- No comments in code
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

- Free to use commercially
- Can modify the code
- Can distribute copies
- Must disclose source
- Must use same license
- Must state changes

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
- [ ] Promo code system
- [ ] Analytics dashboard
- [ ] Multi-language support

### Under Consideration

- [ ] Web dashboard for admins
- [ ] Automated refund system
- [ ] Integration with more payment providers
- [ ] Mobile app companion

## Changelog

### Version 3.0.0 (2026-02-20)

**Added:**
- Profile button — shows total stars purchased, total UAH spent, referral balance
- Referral system with unique per-user invite links (`?start=ref_ID`)
- 1% referral bonus stars credited on each purchase by a referred user
- Real-time referral purchase notification sent to the referrer
- Referral balance withdrawal flow with admin notification
- Withdrawal-specific review type (`withdrawal`)
- Automatic silent review posted to channel 1 hour after purchase if user skips review
- `WithdrawalStates` FSM state group
- `handlers/profile.py` — new handler file for referral and withdrawal logic
- `save_silent_review()` database function for auto-reviews
- New database functions: `set_referrer()`, `get_referrer_id()`, `add_referral_balance()`, `deduct_referral_balance()`, `get_referral_stats()`, `get_user_profile()`
- `update_user_stats()` called on every approved payment to track `total_stars` and `total_uah`

**Changed:**
- Review format: username removed from public posts, buyer identified only by review number (`Покупець #603`)
- Review counter starts at **#603**
- All holiday/seasonal emojis removed from all messages and buttons
- Main menu now includes: Profile, Referral System, Withdraw Stars buttons
- `database.py` users table extended with: `username`, `full_name`, `total_stars`, `total_uah`, `referral_balance`, `referred_by`
- `database.py` reviews table extended with: `review_type` column
- `save_user()` now accepts and stores `username` and `full_name`
- Review auto-increment sequence starts at 602 (first review ID = 603)

**Removed:**
- Username line (`📱 Username: @...`) from public review channel posts
- All holiday emojis (snowflakes, Santa, reindeer, Christmas trees, etc.)

### Version 2.0.0 (2026-02-16)

**Added:**
- Custom star amount input
- Unified pricing (0.84 UAH/star)
- Quick package presets (13, 21, 26, 50)
- Order confirmation before payment
- Hot deal indicator for 50-star package

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

Star this repo if you find it useful!