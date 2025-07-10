from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

read = InlineKeyboardBuilder()
read.row(InlineKeyboardButton(
    text='🗑 Удалить сообщение',
    callback_data='read'
))

info = InlineKeyboardBuilder()
info.row(InlineKeyboardButton(
    text='📖 Исходный код',
    url='https://github.com/evryoneowo/locker'
),       
         InlineKeyboardButton(
    text='📄 Криптография бота',
    url='https://telegra.ph/Locker--Cryptography-07-10'
))