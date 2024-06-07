from aiogram import types

from aiogram.fsm.context import FSMContext

from Tools.GoogleAPITools import GoogleTools
from Tools.BotTools import Tools
from SQL.Tables import MySQLSession, Verify

from States import states_verifiction

import random

from dotenv import load_dotenv

GoogleTools = GoogleTools()
load_dotenv(dotenv_path='.env')
BotTools = Tools()


def verify_code(gmail: str):
    code = random.randint(a=10000, b=99999)
    GoogleTools.gmail_send(to=gmail, text_message=f'Ваш код подтверждения: {code}')
    return code


async def repeat_generate_code(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(generate_code=verify_code(data['gmail']))
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


async def input_gmail(call: types.CallbackQuery, state: FSMContext):
    with MySQLSession.begin() as session:
        if session.query(Verify.gmail).filter_by(user_id=call.from_user.id).first():
            await call.message.answer('Вы уже прошли верефикацию!',
                                      reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                         call_back=['start']))
        else:
            await state.set_state(states_verifiction.StepsVerification.gmail)
            await call.message.answer('Введите вашу Google почту:',
                                      reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                         call_back=['start']))
    await call.answer()
    await call.message.delete()


async def input_code(message: types.Message, state: FSMContext):
    if message.text.split('@')[1] == 'gmail.com' and len(message.text.split('@')) == 2:
        await state.update_data(gmail=message.text)
        data = await state.get_data()
        await state.update_data(generate_code=verify_code(data['gmail']))
        await state.set_state(states_verifiction.StepsVerification.code)
        await message.answer('Введите код подтверждения из письма:\n'
                             '(Проверьте папку "спам", если письма нет во входящих)',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Назад', 'Отправить заново'],
                                 call_back=['start', 'repeat_generate_code_verify']))
    else:
        await state.set_state(states_verifiction.StepsVerification.gmail)
        await message.answer('Для правильно работы бота необходима именно Google почта!\n'
                             'Убедитесь, что в конце адресса почты Вы указали "@gmail.com"\n'
                             'Повторите попытку ввода вашу Google почту:',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                    call_back=['start']))


async def check_data(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    data = await state.get_data()

    if str(data['code']) != str(data['generate_code']):
        await states_verifiction.StepsVerification.code.set()
        await message.answer('Неверный код подтверждения!\n\n'
                             'Введите код подтверждения из письма:',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад', 'Отправить заново'],
                                                                                call_back=['start',
                                                                                           'repeat_generate_code_verify']))
    else:
        try:
            with MySQLSession.begin() as session:
                session.add(Verify(**{"user_id": message.from_user.id,
                                      "gmail": data['gmail']}))
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
        await state.clear()

