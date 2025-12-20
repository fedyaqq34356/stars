Вот исправленная версия вашего `README.md`. Я убрал все лишние заголовки с `#` (хэши), чтобы текст отображался как обычный параграф с жирным выделением и списками. На GitHub это будет выглядеть чисто и аккуратно — без огромных заголовков, но с сохранением структуры, эмодзи и читаемости.

```markdown
⭐ **Telegram Stars & Premium Bot**

A professional Telegram bot for selling **Telegram Stars** and **Telegram Premium** subscriptions with discounts.  
Supports payments via TON (cryptocurrency) and Ukrainian bank cards (UAH).  

Built with **aiogram 3.x**, SQLite database, and integration with an external delivery API.

**Key Features**

- Stars packages from 50 to 10,000 ⭐ (with highlighted hot deals)
- Telegram Premium subscriptions for 3, 6, or 12 months
- Payment options: card (manual admin approval) or TON Connect
- Mandatory channel subscription before purchase
- Review system with automatic posting to a public channel
- Admin tools: statistics, broadcasts, bot restart
- Automatic cleanup of expired orders

**Installation**

```bash
git clone https://github.com/fedyaqq34356/stars.git
cd stars

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

**Configure .env**

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321
SPLIT_API_TOKEN=your_token
SPLIT_API_URL=https://api.example.com
REVIEWS_CHANNEL_ID=-1001234567890
MAIN_CHANNEL_ID=-1001234567890
CARD_NUMBER=1234567890123456
RESTART_ON_ERROR=true
```

**Run the Bot**

```bash
python main.py
```

**Customization**

- Edit prices and packages in `config.py` (via the `STAR_PRICES` dictionary).
- Modify button texts and menus in `keyboards.py`.  
  **Important**: `callback_data` must exactly match the keys in `STAR_PRICES`.

**License**

This project is licensed under the **GNU General Public License v3.0 (GPLv3)** — see the LICENSE file for details.

---

⭐ If you find this project useful, consider giving it a star!  
Happy deploying! 🚀
