# Locker
## Description
Locker is a password manager Telegram bot written with aiogram.
It has cryptographic protection. You can trust it, or easily deploy your own instance to verify everything yourself.

## Main instance
The main instance of the bot is https://t.me/lockerpassbot. 
It has latest updates of the bot and works 24/7.
> [!WARNING]
> If you lost your master key you won't able to get your passwords!

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

4. Create a PostgreSQL database:

    Make sure you have PostgreSQL installed and running.  
    Create a new database named `lockerbot`:

    ```bash
    createdb lockerbot
    ```

    Or connect to PostgreSQL and run:

    ```sql
    CREATE DATABASE lockerbot;
    ```

5. Copy the .env example:

```bash
cp .env.example .env
```

6. Configure `.env` with your own settings.

7. Run the bot
```bash
python3 -m lockerbot
```
or
```bash
cd lockerbot && python3 main.py
```

🎉 Congratulations - you're up and running!

## Security

The bot’s database stores your passwords only in encrypted form. Only you can decrypt them using master-password. Also, the bot automatically deletes all messages that contain your passwords, so no one can steal them even if someone gains access to your Telegram account.
