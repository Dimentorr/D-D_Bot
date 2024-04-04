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
    query_log = [f'SELECT is_login FROM users WHERE user_id = {call.from_user.id}']
    # if con.work_with_MySQL(query_log):
    if l_con.work_with_SQLite(query_log):
        await call.message.answer('Вы уже имеете созданного пользователя!')
    else:
        await state.set_state(states_reg_log.StepsReg.name)
        await call.message.answer('Введите логин:',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                     call_back=['Back']))
    await call.answer()
    await call.message.delete()


async def input_password(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(states_reg_log.StepsReg.password)
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['Back']))


async def input_repeat_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(states_reg_log.StepsReg.repeat_password)
    await message.answer('Введите пароль повторно:',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['Back']))


async def check_data(message: types.Message, state: FSMContext):
    await state.update_data(repeat_password=message.text)
    data = await state.get_data()

    if data['repeat_password'] != data['password']:
        await message.answer('Пароли не совпадают! Повторите изначальный пароль.')
        await states_reg_log.StepsReg.password.set()
        await message.answer('Введите пароль:',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['Back']))
    else:
        name = data['name']
        password = data['password']
        try:
            # con.work_with_MySQL([f'INSERT INTO users(user_id, name_user, password, is_login)'
            #                     f' VALUES("{message.from_user.id}", "{name}", "{password}", 1)'])
            l_con.work_with_SQLite([f'INSERT INTO users(user_id, name_user, password, is_login)'
                                 f' VALUES("{message.from_user.id}", "{name}", "{password}", 1)'])
            await message.answer(f'Добро пожаловать в D&D бота!\n'
                                 f'Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(
                                     buttons=['Персонажи', 'Компании', 'Верификация'],
                                     call_back=['Character', 'Story', 'verify'])
                                 )
        except Exception as err:
            await message.answer(f'''Произошла ошибка:
{err}

Сообщите об этом администратору и попробуйте повторить попытку позже''',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['В начало'],
                                                                                    call_back=['start'])
                                 )
        await state.clear()

