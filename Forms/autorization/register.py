from aiogram import types

from aiogram.dispatcher import FSMContext

from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from States import states_reg_log


BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def input_login(call: types.CallbackQuery):
    query_log = f'SELECT is_login FROM users WHERE user_id = {call.from_user.id}'
    if con.work_with_MySQL(query_log):
        await call.message.answer('Вы уже имеете созданного пользователя!')
    else:
        await states_reg_log.StepsReg.name.set()
        await call.message.answer('Введите логин:',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=['Назад'],
                                      call_back=['Back'],
                                      message=call.message))


async def input_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await states_reg_log.StepsReg.next()
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_inline_keyboard(
                             buttons=['Назад'],
                             call_back=['Back'],
                             message=message))


async def input_repeat_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await states_reg_log.StepsReg.next()
    await message.answer('Введите пароль повторно:',
                         reply_markup=BotTools.construction_inline_keyboard(
                             buttons=['Назад'],
                             call_back=['Back'],
                             message=message))


async def check_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['repeat_password'] = message.text

    if data['repeat_password'] != data['password']:
        await message.answer('Пароли не совпадают! Повторите изначальный пароль.')
        await states_reg_log.StepsReg.password.set()
        await message.answer('Введите пароль:',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Назад'],
                                 call_back=['Back'],
                                 message=message))
    else:
        name = data['name']
        password = data['password']
        try:
            con.work_with_MySQL(f'INSERT INTO users(user_id, name_user, password, is_login)'
                                f' VALUES("{message.from_user.id}", "{name}", "{password}", 1)')
            await message.answer(f'Добро пожаловать в D&D бота!\n'
                                 f'Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(
                                     buttons=['Персонажи', 'Компании', 'Верификация'],
                                     call_back=['Character', 'Story', 'verify'],
                                     message=message)
                                 )
        except Exception as err:
            await message.answer(f'''Произошла ошибка:
{err}

Сообщите об этом администратору и попробуйте повторить попытку позже''',
                                 reply_markup=BotTools.construction_inline_keyboard(
                                     buttons=['В начало'],
                                     call_back=['start'],
                                     message=message)
                                 )
        await state.finish()

