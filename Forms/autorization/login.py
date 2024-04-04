from aiogram import types

from aiogram.fsm.context import FSMContext

from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from Tools.SQLiteTools import Connection as LiteConnection

from States import states_reg_log


BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))
l_con = LiteConnection(path='file/db/bot_base.db')


async def input_login(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.set_state(states_reg_log.StepsLogin.name)
    await call.message.answer('Введите логин:',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                 call_back=['start']))


async def input_password(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(states_reg_log.StepsLogin.password)
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['start']))


async def check_data(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    name = data['name']
    password = data['password']
    # if con.work_with_MySQL([f'SELECT id FROM users WHERE name_user = "{name}" AND password = "{password}"']):
    if l_con.work_with_SQLite([f'SELECT id FROM users WHERE name_user = "{name}" AND password = "{password}"']):
        del_keyboard = types.ReplyKeyboardRemove()
        await message.answer('Добро пожаловать в D&D бота!', reply_markup=del_keyboard)
        await message.answer('Пожалуйста, выберите интерисующий вас пункт',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Персонажи', 'Компании', 'Верификация'],
                                 call_back=['Character', 'Story', 'verify']))
        # con.work_with_MySQL([f'UPDATE users SET is_login = 1 WHERE name_user = "{name}" AND password = "{password}"'])
        l_con.work_with_SQLite(
            [f'UPDATE users SET is_login = 1 WHERE name_user = "{name}" AND password = "{password}"'])
    else:
        await message.answer('Неверный логин или пароль!'
                             'Пожалуйста попробуйте сново',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Попробовать сново', 'Регистрация'], call_back=['Login', 'Registration']))
    await state.clear()
