from asyncio import run
from logging import basicConfig, INFO
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from dotenv import load_dotenv

from .handlers import router

async def main():
    # Logging configuration
    basicConfig(level=INFO)

    # Getting botapi token
    load_dotenv(dotenv_path='../.env')
    token = getenv('BOT_TOKEN')

    # Initialization
    bot = Bot(token=token, 
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    run(main())
