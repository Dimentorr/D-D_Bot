from aiogram import types

from aiogram.fsm.context import FSMContext

from Tools.MySqlTools import Connection
from Tools.BotTools import Tools
from Tools.SQLiteTools import Connection as LiteConnection
from Tools.YoomoneyTools import YooMoney

from States import states_donate

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

BotTools = Tools()
YooMoney = YooMoney()
# con = Connection(host=env.read_json_data('DB_host'),
#                  port=env.read_json_data('DB_port'),
#                  database_name=env.read_json_data('DB_database'),
#                  user=env.read_json_data('DB_user'),
#                  password=env.read_json_data('DB_password'))
l_con = LiteConnection(path=os.getenv('path_sqlite_db'))


async def info(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(states_donate.StepsDonate.info)
    await call.message.answer('Привет, спасибо, что используешь этого бота!\n'
                              'Я надеюсь, что он тебе нравится и помогает в проведении или участии в играх)\n\n'
                              'Если ты хочешь поддержать разработку материально, то перейдя дальше с помощью кнопки '
                              '"Продолжить", ты сможешь ввести сумму, которую ты готов пожертвовать\n\n'
                              'Куда пойдут эти деньги?\n'
                              'В первую очередь на оплату хостинга, где на данный момент расположен бот,'
                              ' а так же на будущие обновления бота)\n\n'
                              'В любом случаи ещё раз благодарю за использование моего бота!)',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=[['Продолжить'], ['Назад']],
                                                                                 call_back=[['get_info'], ['start']]))
    await call.answer()
    await call.message.delete()


async def input_cost(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(info='yes')
    await state.set_state(states_donate.StepsDonate.cost)
    await call.message.answer('Введите сумму:',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['start'])
                              )


async def value_error_repeat_cost(message: types.Message, state: FSMContext):
    await state.set_state(states_donate.StepsDonate.cost)
    await message.answer('Некоректный ввод!\n',
                         'Введите сумму:',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'], call_back=['start']))


async def check_data(message: types.Message, state: FSMContext):
    await state.update_data(cost=message.text)
    data = await state.get_data()
    try:
        cost = float(data['cost'].replace(',', '.'))
        url = YooMoney.create_cheque(cost=cost, receiver=os.getenv('YOOMONEY_RECEIVER'), message='На развитие бота')
        await message.answer(f'Заранее благодарю за поддержку!',
                             reply_markup=BotTools.construction_inline_keyboard_with_link(
                                 list_name=[['Ссылка на оплату']],
                                 list_link=[[url]]))
        await state.clear()
    except ValueError:
        print('err')
        await message.answer('Некоректный ввод!')
