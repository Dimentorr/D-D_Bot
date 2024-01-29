import asyncio
import logging
from aiogram import Bot, Dispatcher, types

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from States import states_reg_log


data = dict()
BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def input_login(message: types.Message, state: FSMContext, bot: Bot):
    query_log = f'SELECT is_login FROM users WHERE user_id = {message.from_user.id}'
    if con.work_with_MySQL(query_log):
        await message.answer('Вы уже имеете созданного пользователя!')
    else:
        await message.answer('Введите логин:',
                             reply_markup=BotTools.construction_keyboard(
                                 buttons=['Назад'],
                                 call_back=['Back']))
        await state.set_state(states_reg_log.StepsReg.NAME)


async def input_password(message: types.Message, state: FSMContext, bot: Bot):
    data['name'] = message.text
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_keyboard(
                             buttons=['Назад'],
                             call_back=['Back']))
    await state.set_state(states_reg_log.StepsReg.PASSWORD)


async def input_repeat_password(message: types.Message, state: FSMContext, bot: Bot):
    data['password'] = message.text
    await message.answer('Введите пароль повторно:',
                         reply_markup=BotTools.construction_keyboard(
                             buttons=['Назад'],
                             call_back=['Back']))
    await state.set_state(states_reg_log.StepsReg.REPEAT_PASSWORD)


async def check_data(message: types.Message, state: FSMContext, bot: Bot):
    name = data['name']
    password = message.text

    if message.text != data['password']:
        await message.answer('Пароли не совпадают! Повторите изначальный пароль.')
        await message.answer('Введите пароль:',
                             reply_markup=BotTools.construction_keyboard(
                                 buttons=['Назад'],
                                 call_back=['Back']))
        await state.set_state(states_reg_log.StepsReg.PASSWORD)
    else:
        try:
            con.work_with_MySQL(f'INSERT INTO users(user_id, name_user, password, is_login)'
                                f' VALUES({message.from_user.id}, "{name}", "{password}", 1)')
            del_keyboard = types.ReplyKeyboardRemove()
            await message.answer('Добро пожаловать в D&D бота!', reply_markup=del_keyboard)
            await message.answer('Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(
                                     buttons=['Персонажи', 'Компании'],
                                     call_back=['Character', 'Story'])
                                 )
        except Exception as err:
            await message.answer(f'''Произошла ошибка:
{err}

Сообщите об этом администратору и попробуйте повторить попытку позже''')

