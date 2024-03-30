from aiogram import types

from aiogram.dispatcher import FSMContext

from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.GoogleAPITools import GoogleTools
from Tools.BotTools import Tools

from States import states_verifiction

import random

GoogleTools = GoogleTools()
BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


def verify_code(gmail: str):
    code = random.randint(a=10000, b=99999)
    GoogleTools.gmail_send(to=gmail, text_message=f'Ваш код подтверждения: {code}')
    return code


async def repeat_generate_code(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['generate_code'] = verify_code(data['gmail'])
    await call.message.answer(f'Введите новый код подтверждения из письма:',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                 call_back=['start']))
    await call.answer()
    await call.message.delete()


async def start_verify(call: types.CallbackQuery):
    await call.message.answer(f'Для работоспособности некоторых функций бота необходима ваша Google почта,\n'
                              f'Ничего, кроме вашего адресса почты Не будет сохранено и/или отслеживаться',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад', 'Продолжить'],
                                                                                 call_back=['start', 'input_gmail']))
    await call.answer()
    await call.message.delete()


async def input_gmail(call: types.CallbackQuery):
    query_log = ([f'SELECT gmail FROM verify '
                 f'WHERE user_id = '
                 f'(SELECT id FROM users WHERE user_id = {call.from_user.id})'])
    if con.work_with_MySQL(query_log):
        await call.message.answer('Вы уже прошли верефикацию!',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                     call_back=['start']))
    else:
        await states_verifiction.StepsVerification.gmail.set()
        await call.message.answer('Введите вашу Google почту:',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                     call_back=['start']))
    await call.answer()
    await call.message.delete()


async def input_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.split('@')[1] == 'gmail.com' and len(message.text.split('@')) == 2:
            data['gmail'] = message.text
            data['generate_code'] = verify_code(data['gmail'])
            await states_verifiction.StepsVerification.next()
            await message.answer('Введите код подтверждения из письма:',
                                 reply_markup=BotTools.construction_inline_keyboard(
                                     buttons=['Назад', 'Отправить заново'],
                                     call_back=['start', 'repeat_generate_code_verify']))
        else:
            await states_verifiction.StepsVerification.gmail.set()
            await message.answer('Для правильно работы бота необходима именно Google почта!\n'
                                 'Убедитесь, что в конце адресса почты Вы указали "@gmail.com"\n'
                                 'Повторите попытку ввода вашу Google почту:',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                    call_back=['start']))


async def check_data(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code'] = message.text

    if str(data['code']) != str(data['generate_code']):
        await states_verifiction.StepsVerification.code.set()
        await message.answer('Неверный код подтверждения!\n\n'
                             'Введите код подтверждения из письма:',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад', 'Отправить заново'],
                                                                                call_back=['start',
                                                                                           'repeat_generate_code_verify']))
    else:
        gmail = data['gmail']
        user_id = con.work_with_MySQL([f'SELECT id FROM users '
                                      f'WHERE user_id = "{message.from_user.id}"'])[0][0]
        try:
            con.work_with_MySQL([f'INSERT INTO verify(gmail, user_id)'
                                f' VALUES("{gmail}", {user_id})'])
            await message.answer(f'Добро пожаловать в D&D бота!\n'
                                 f'Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['Персонажи', 'Компании'],
                                                                                    call_back=['Character', 'Story'])
                                 )
        except Exception as err:
            await message.answer(f'''Произошла ошибка:
{err}

Сообщите об этом администратору и попробуйте повторить попытку позже''',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['В начало'],
                                                                                    call_back=['start'])
                                 )
        await state.finish()

