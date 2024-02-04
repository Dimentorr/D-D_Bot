from aiogram import Bot, Dispatcher, types

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
    await states_reg_log.StepsLogin.name.set()
    await call.message.answer('Введите логин:',
                              reply_markup=BotTools.construction_inline_keyboard(
                                  buttons=['Назад'],
                                  call_back=['Back'],
                                  message=call.message))


async def input_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await states_reg_log.StepsLogin.next()
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_inline_keyboard(
                             buttons=['Назад'],
                             call_back=['Back'],
                             message=message))


async def check_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
    name = data['name']
    password = data['password']
    if con.work_with_MySQL(f'SELECT id FROM users WHERE name_user = "{name}" AND password = "{password}"'):
        del_keyboard = types.ReplyKeyboardRemove()
        await message.answer('Добро пожаловать в D&D бота!', reply_markup=del_keyboard)
        await message.answer('Пожалуйста, выберите интерисующий вас пункт',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Персонажи', 'Компании'],
                                 call_back=['Character', 'Story'],
                                 message=message))
        con.work_with_MySQL(f'UPDATE users SET is_login = 1 WHERE name_user = "{name}" AND password = "{password}"')
    else:
        await message.answer('Неверный логин или пароль!'
                             'Пожалуйста попробуйте сново',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Попробовать сново', 'Регистрация'],
                                 call_back=['Login', 'Registration'],
                                 message=message))
    await state.finish()
