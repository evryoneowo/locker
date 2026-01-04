from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

read = InlineKeyboardBuilder()
read.row(InlineKeyboardButton(
    text='🗑 Удалить сообщение',
    callback_data='read'
))

