import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

# from aiogram import F
# from aiogram.fsm.context import FSMContext
# from aiogram.filters import Command
# from aiogram.fsm.state import StatesGroup, State

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from States import states_connect_to

BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def linc_group_id(call: types.CallbackQuery):
    await states_connect_to.StepsConnectTo.id.set()
    await call.message.answer(f'Введите id компании\n'
                              f'(попросите вашего Мастера сообщить его вам, если этого не произошло ранее)',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['На главную'],
                                 call_back=['start'],
                                 message=call.message)
                              )
    await call.answer()
    await call.message.delete()


async def linc_group_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['group_id'] = message.text
    await states_connect_to.StepsConnectTo.next()
    await message.answer(f'Введите пароль от комнаты\n'
                         f'(попросите вашего Мастера сообщить его вам, если этого не произошло ранее)',
                         reply_markup=BotTools.construction_inline_keyboard(
                             buttons=['На главную'],
                             call_back=['start'],
                             message=message)
                         )


async def linc_group_check(message: types.Message, state: FSMContext):
    from main import bot
    async with state.proxy() as data:
        data['password'] = message.text
    group = data['group_id']
    password = data['password']
    if con.work_with_MySQL(f'SELECT id FROM game_stories '
                           f'WHERE id_group = {group} AND '
                           f'password = {password}'):
        expire_date = datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(group, expire_date.timestamp, 1)
        # print(link)

        await message.answer(f'Приятной игры!\n'
                             f'Ваша ссылка для подключения к группе - {link.invite_link}',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['На главную'],
                                 call_back=['start'],
                                 message=message)
                             )
    else:
        await message.answer('Неверный id или пароль группы!',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Попробовать сново'],
                                          ['На главную']],
                                 call_back=[['connect_to'],
                                            ['start']],
                                 message=message))
        await state.finish()