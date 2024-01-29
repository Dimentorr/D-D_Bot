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
    print('i this')
    # query_log = f'SELECT is_login FROM users WHERE user_id = {message.from_user.id}'
    # if con.work_with_MySQL(query_log):
    await message.answer('Введите логин:',
                         reply_markup=BotTools.construction_keyboard(
                             buttons=['Назад'],
                             call_back=['Back']))
    await state.set_state(states_reg_log.StepsLogin.NAME)


async def input_password(message: types.Message, state: FSMContext, bot: Bot):
    data['name'] = message.text
    await message.answer('Введите пароль:',
                         reply_markup=BotTools.construction_keyboard(
                             buttons=['Назад'],
                             call_back=['Back']))
    await state.set_state(states_reg_log.StepsLogin.PASSWORD)


async def check_data(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    name = data['name']
    password = message.text
    # id_user = con.work_with_MySQL(f'SELECT id FROM users WHERE name_user = "{name}" AND password = "{password}"')
    # print(id_user[0][0])
    if con.work_with_MySQL(f'SELECT id FROM users WHERE name_user = "{name}" AND password = "{password}"'):
        del_keyboard = types.ReplyKeyboardRemove()
        await message.answer('Добро пожаловать в D&D бота!', reply_markup=del_keyboard)
        await message.answer('Пожалуйста, выберите интерисующий вас пункт',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Персонажи', 'Компании'],
                                 call_back=['Character', 'Story'])
                             )
        con.work_with_MySQL(f'UPDATE users SET is_login = 1 WHERE name_user = "{name}" AND password = "{password}"')
    else:
        await message.answer('Неверный логин или пароль!'
                             'Пожалуйста попробуйте сново',
                             reply_markup=BotTools.construction_keyboard(
                                 buttons=['Попробовать сново', 'Регистрация'],
                                 call_back=['NewTry', 'Reg']))
