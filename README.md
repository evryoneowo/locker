# Locker
## Description
Locker is a password manager Telegram bot written with aiogram.
It has cryptographic protection. You can trust it, or easily deploy your own instance to verify everything yourself.

## Main instance
The main instance of the bot is t.me/lockerpassbot
It has latest updates of the bot and works 24/7.

## Using

It\`s easy!

1. Clone the repo:

```bash
git clone https://github.com/evryoneowo/locker && cd locker
```

2. Set up a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Copy the .env example:

```bash
cp .env.example .env
```

5. Configure `.env` with your own settings.

6. Run the bot
```bash
python3 -m lockerbot
```

🎉 Congratulations - you're up and running!

## Security

The bot’s database stores your passwords only in encrypted form. Only you can decrypt them using master-password. Also, the bot automatically deletes all messages that contain your passwords, so no one can steal them even if someone gains access to your Telegram account.
