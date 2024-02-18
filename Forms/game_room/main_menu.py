import asyncio
import logging
from aiogram import Bot, Dispatcher, types

# from aiogram import F
# from aiogram.fsm.context import FSMContext
# from aiogram.filters import Command
# from aiogram.fsm.state import StatesGroup, State

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from States import states_reg_log

BotTools = Tools()


async def first_menu_game_function(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Мои компании', 'Доступные компании'],
                                          ['Создать новую', 'Присоединиться'],
                                          ['На главную']],
                                 call_back=[['GM_list', 'player_list'],
                                            ['create_new_game', 'connect_to'],
                                            ['start']],
                                 message=call.message)
                              )
    await call.answer()
    await call.message.delete()
