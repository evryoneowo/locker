from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import db, crypto, keyboards
from .menu import *

@start
@router.message(Command('start'))
async def startcmd(msg: Message, _=None):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    txt = '''<b>🔐 Locker</b>

Удобный менеджер паролей. Предусмотрена <b>криптографическая</b> защита, а также Вы можете запустить свой инстанс бота, так как он имеет открытый <b>исходный код</b>!'''

    if not user:
        txt += '\n\nУкажите мастер-пароль в настройках.'
    
    keyboard = start.keyboard(msg)
    keyboard.row(InlineKeyboardButton(
        text='📖 Исходный код',
        url='https://github.com/evryoneowo/locker'
    ),       
             InlineKeyboardButton(
        text='📄 Криптография бота',
        url='https://telegra.ph/Locker--Cryptography-07-10'
    ))


    await msg.answer(txt,
                     reply_markup=keyboard.as_markup())

@settings
async def on_settings(msg: Message, keyboard: InlineKeyboardBuilder):
    await msg.answer('⚙️ <b>Настройки</b>',
                     reply_markup=keyboard.as_markup())

@manage
async def on_manage(msg: Message, keyboard: InlineKeyboardBuilder):
    user = db.session.query(db.User).filter(db.User.user_id == msg.chat.id).first()

    if not user:
        await msg.answer('У Вас не задан мастер-пароль')
        return

    txt = '<b>Сервисы:</b>\n\n'
    for i in user.passwords:
        txt += f'<code>{i.service}</code>\n'
    
    await msg.answer(txt,
                     reply_markup=keyboard.as_markup())

@master.arg('Введите новый мастер-пароль')
async def mastercmd(msg: Message, args):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if user:
        return True

    password = args[0]

    hashed, salt = crypto.hash_password(password)

    user = db.User(
        user_id = msg.from_user.id,
        password_hash = hashed,
        salt = salt
    )

    db.session.add(user)
    db.session.commit()

    await msg.answer(f'✅ <b>Мастер-пароль установлен</b>\n\nХеш: <code>{hashed}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>')
    
    await master.cancel(msg)
    return True

@master.arg('Введите старый мастер-пароль')
async def newmastercmd(msg: Message, args):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()
    
    password, master = args

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    hashed, salt = crypto.hash_password(password)

    user.password_hash, user.salt = hashed, salt

    for passw in db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id):
        decrypted = crypto.decrypt_password(master, passw.salt, passw.password_enc, passw.nonce)
        
        encrypted, salt, nonce = crypto.encrypt_password(password, decrypted)

        passw.password_enc = encrypted
        passw.salt = salt
        passw.nonce = nonce
    
    db.session.commit()

    txt = f'✅ <b>Мастер-пароль изменен, пароли пересчитаны</b>\n\nХеш: <code>{hashed}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>'

    await msg.answer(txt)
    return True

@add.arg('Введите название сервиса')
async def on_add_service(msg: Message, args):
    return True

@add.arg('Введите логин')
async def on_add_login(msg: Message, args):
    return True

@add.arg('Введите пароль ("gen", чтобы сгенерировать)')
async def on_add_paswwd(msg: Message, args):
    return True

@add.arg('Введите мастер-пароль')
async def on_add_master(msg: Message, args):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    service, login, password, master = args

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    if password == 'gen':
        password = crypto.gen_password()

        await msg.answer(f'ℹ️ <b>Сгенерированный пароль:</b>\n<code>{password}</code>',
                         reply_markup=keyboards.read.as_markup())

    passw = db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id, db.Password.service == service).first()

    encrypted, salt, nonce = crypto.encrypt_password(master, password)

    if passw:
        passw.login = login
        passw.password_enc = encrypted
        passw.salt = salt
        passw.nonce = nonce
    else:
        new_password = db.Password(
            user_id=user.user_id,
            service=service,
            login=login,
            password_enc=encrypted,
            salt=salt,
            nonce=nonce
        )

        db.session.add(new_password)
    db.session.commit()

    action = 'изменен' if passw else 'добавлен'

    txt = f'✅ <b>Сервис {service} {action}!</b>\n\nЗашифрованный пароль: <code>{crypto.bytestostr(encrypted)}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>\nNonce: <code>{crypto.bytestostr(nonce)}</code>'

    await msg.answer(txt)
    return True

@get.arg('Введите название сервиса')
async def on_get_service(msg: Message, args):
    return True

@get.arg('Введите мастер-пароль')
async def on_get_master(msg: Message, args):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    service, master = args

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    password = db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id, db.Password.service == service).first()

    if not password:
        await msg.answer('❗️ <b>Нет такого пароля!</b>')
        
        return True
    
    decrypted = crypto.decrypt_password(master, password.salt, password.password_enc, password.nonce)

    await msg.answer(f'<b>{service}</b>\n\nЛогин: <code>{password.login}</code>\nПароль: <code>{decrypted}</code>',
                     reply_markup=keyboards.read.as_markup())

    return True

@delete.arg('Введите название сервиса')
async def on_del_service(msg: Message, args):
    return True

@delete.arg('Введите мастер-пароль')
async def on_del_master(msg: Message, args):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    service, master = args

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    passwords = db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id, db.Password.service == service)

    if not passwords:
        await msg.answer('❗️ <b>Нет таких записей!</b>')

        return True
    
    passwords.delete()
    db.session.commit()

    await msg.answer('✅ <b>Записи успешно удалены!</b>')

    return True

@handle(data == 'read')
async def on_read(cq: CallbackQuery):
    await cq.message.delete()

register()

