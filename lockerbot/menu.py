from aiogram import Router
from aiogramui import *

router = Router()
init(router)

start = Root('start', '⬅️')

manage = start.page('📝 Управление паролями')
add = manage.dialog('➕ Добавить / Изменить')
get = manage.dialog('👀 Посмотреть')
delete = manage.dialog('🗑 Удалить')

settings = start.page('⚙️ Настройки')
master = settings.dialog('🔐 Мастер-пароль')

