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
    # check_params_group = con.work_with_MySQL(f'SELECT id FROM game_stories '
    #                        f'WHERE id_group = {group} AND '
    #                        f'password = {password}')
    try:
        check_GM = con.work_with_MySQL(f'SELECT user_id FROM users '
                                       f'WHERE id = (SELECT GM_id FROM game_stories '
                                       f'WHERE id = (SELECT id FROM game_stories '
                                       f'WHERE id_group = {group} AND '
                                       f'password = {password})'
                                       f')')[0][0]
    except IndexError:
        check_GM = -1
    try:
        check_user = con.work_with_MySQL(f'SELECT user_id FROM users '
                                         f'WHERE id = (SELECT player_id FROM players_stories '
                                         f'WHERE id = (SELECT id FROM game_stories '
                                         f'WHERE id_group = {group} AND '
                                         f'password = {password})'
                                         f')')[0][0]
    except IndexError:
        check_user = -1
    if (message.from_user.id != check_GM) and (message.from_user.id != check_user):
        expire_date = datetime.now() + timedelta(days=1)
        link = await bot.create_chat_invite_link(group, expire_date.timestamp, 1)

        await message.answer(f'Приятной игры!\n'
                             f'Ваша ссылка для подключения к группе - {link.invite_link}',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['На главную'],
                                 call_back=['start'],
                                 message=message)
                             )
    elif (message.from_user.id == check_GM) or (message.from_user.id == check_user):
        await message.answer('Вы уже являетесь участником этой компании!',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['На главную'],
                                 call_back=['start'],
                                 message=message))
    else:
        await message.answer('Неверный id или пароль группы!',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Попробовать сново'],
                                          ['На главную']],
                                 call_back=[['connect_to'],
                                            ['start']],
                                 message=message))
    await state.finish()