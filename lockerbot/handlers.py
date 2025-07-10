from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from . import db, crypto, keyboards

router = Router()

@router.message(Command('help'))
async def helpcmd(msg: Message):
    await msg.answer('''<b>📃 Доступные команды</b>

/help - список команд
/master [pass] - установить мастер-пароль, gen в поле пароля для автоматической генерации
/newmaster [newpass] [oldpass] - установить новый мастер-пароль, gen в поле пароля для автоматической генерации
/add [service] [login] [pass] [masterpass] - добавить / изменить запись, gen в поле пароля для автоматической генерации
/get [service] [masterpass] - получить запись
/services - показать все записанные сервисы
/del [service] [masterpass] - удалить запись
/deletemyaccount [masterpass] - удалить аккаунт
/togglecrypto - вкл/выкл отображение криптографический данных''')

@router.message(Command('start'))
async def startcmd(msg: Message):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    txt = '''<b>🔐 Locker</b>

Удобный менеджер паролей. Предусмотрена <b>криптографическая</b> защита, а также ты можешь запустить свой инстанс бота, так как он имеет открытый <b>исходный код</b>!
/help - список команд'''

    if not user:
        txt += '\n\nНапиши /master [pass] чтобы установить мастер-пароль.'
    
    await msg.answer(txt,
                     reply_markup=keyboards.source.as_markup())

@router.message(Command('master'))
async def mastercmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if user:
        await msg.answer('❗️ <b>У тебя уже стоит мастер-пароль!</b>')
        return
    
    if len(msg.text.split()) != 2:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /master [pass]')
        return

    password = msg.text.split()[1]
    
    if password == 'gen':
        password = crypto.gen_password()

        await msg.answer(f'ℹ️ <b>Сгенерированный мастер-пароль:</b>\n<code>{password}</code>\n\nСохрани его!',
                         reply_markup=keyboards.read.as_markup())

    hashed, salt = crypto.hash_password(password)

    user = db.User(
        user_id = msg.from_user.id,
        togglecrypto = True,
        password_hash = hashed,
        salt = salt
    )

    db.session.add(user)
    db.session.commit()

    await msg.answer(f'✅ <b>Мастер-пароль установлен</b>\n\nХеш: <code>{hashed}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>\n\nТеперь ты можешь использовать /add [service] [login] [pass] [masterpass]')

@router.message(Command('newmaster'))
async def newmastercmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет мастер пароля!</b>')
        return
    
    if len(msg.text.split()) != 3:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /newmaster [newpass] [oldpass]')
        return
    
    password, master = msg.text.split()[1:]

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    if password == 'gen':
        password = crypto.gen_password()

        await msg.answer(f'ℹ️ <b>Сгенерированный новый мастер-пароль:</b>\n<code>{password}</code>\n\nСохрани его!',
                         reply_markup=keyboards.read.as_markup())
    
    hashed, salt = crypto.hash_password(password)

    user.password_hash, user.salt = hashed, salt

    for passw in db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id):
        decrypted = crypto.decrypt_password(master, passw.salt, passw.password_enc, passw.nonce)
        
        encrypted, salt, nonce = crypto.encrypt_password(password, decrypted)

        passw.password_enc = encrypted
        passw.salt = salt
        passw.nonce = nonce
    
    db.session.commit()

    txt = f'✅ <b>Мастер-пароль изменен, пароли пересчитаны</b>'
    
    if user.togglecrypto:
        txt += f'\n\nХеш: <code>{hashed}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>'

    await msg.answer(txt)

@router.message(Command('add'))
async def addcmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет мастер-пароля!</b> Используй /master [pass]')
        return
    
    if len(msg.text.split()) != 5:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /add [service] [login] [pass] [masterpass]')
        return

    service, login, password, master = msg.text.split()[1:]

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

    txt = f'✅ <b>Сервис {service} {action}!</b>'

    if user.togglecrypto:
        txt += f'\n\nЗашифрованный пароль: <code>{crypto.bytestostr(encrypted)}</code>\nСоль: <code>{crypto.bytestostr(salt)}</code>\nNonce: <code>{crypto.bytestostr(nonce)}</code>'

    await msg.answer(txt)

@router.message(Command('get'))
async def getcmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет мастер-пароля!</b> Используй /master [pass]')
        return
    
    if len(msg.text.split()) != 3:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /get [service] [masterpass]')
        return

    service, master = msg.text.split()[1:]

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    password = db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id, db.Password.service == service).first()

    if not password:
        await msg.answer('❗️ <b>Нет такого пароля!</b> Используй /add [service] [login] [pass] [masterpass] чтобы создать.')
        return
    
    decrypted = crypto.decrypt_password(master, password.salt, password.password_enc, password.nonce)

    await msg.answer(f'<b>{service}</b>\n\nЛогин: <code>{password.login}</code>\nПароль: <code>{decrypted}</code>',
                     reply_markup=keyboards.read.as_markup())

@router.message(Command('services'))
async def servicescmd(msg: Message):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет мастер-пароля!</b> Используй /master [pass]')
        return
    
    txt = '<b>Сервисы:</b>\n\n'
    for i in user.passwords:
        txt += f'<code>{i.service}</code>\n'
    
    await msg.answer(txt)

@router.message(Command('del'))
async def delcmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет мастер-пароля!</b> Используй /master [pass]')
        return
    
    if len(msg.text.split()) != 3:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /del [service] [masterpass]')
        return

    service, master = msg.text.split()[1:]

    if not crypto.check_password(master, user.salt, user.password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return
    
    passwords = db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id, db.Password.service == service)

    if not passwords:
        await msg.answer('❗️ <b>Нет таких записей!</b>')
        return
    
    passwords.delete()
    db.session.commit()

    await msg.answer('✅ <b>Записи успешно удалены!</b>')

@router.message(Command('deletemyaccount'))
async def deletemyaccountcmd(msg: Message):
    await msg.delete()

    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id)

    if not user.first():
        await msg.answer('❗️ <b>У тебя нет аккаунта!</b> Используй /master [pass]')
        return
    
    if len(msg.text.split()) != 2:
        await msg.answer('❗️ <b>Синтаксис команды:</b> /deletemyaccount [masterpass]')
        return

    master = msg.text.split()[1]

    if not crypto.check_password(master, user.first().salt, user.first().password_hash):
        await msg.answer('❗️ <b>Неверный мастер-пароль!</b>')
        return

    db.session.query(db.Password).filter(db.Password.user_id == msg.from_user.id).delete()
    user.delete()
    
    db.session.commit()

    await msg.answer('✅ <b>Аккаунт успешно удален!</b>')

@router.message(Command('togglecrypto'))
async def togglecryptocmd(msg: Message):
    user = db.session.query(db.User).filter(db.User.user_id == msg.from_user.id).first()

    if not user:
        await msg.answer('❗️ <b>У тебя нет аккаунта!</b> Используй /master [pass]')
        return
    
    state = not user.togglecrypto
    user.togglecrypto = state

    db.session.commit()

    await msg.answer(f'ℹ️ Отображение криптографических данных: <b>{"вкл" if state else "выкл"}</b>')

@router.callback_query()
async def on_cq(cq: CallbackQuery):
    if cq.data == 'read':
        await cq.message.delete()
