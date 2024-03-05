import asyncio
import logging
from aiogram import Bot, executor, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

# from aiogram import F
# from aiogram.fsm.context import FSMContext
# from aiogram.filters import Command
# from aiogram.fsm.state import StatesGroup, State

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


async def menu_create(call: types.CallbackQuery):
    await call.message.answer(f'Создание персонажа:\n'
                              f'(По умолчанию для имени игрока используется имя, которое вы указывали, при регистрации)',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Имя персонажа', 'Имя игрока', 'Класс'],
                                          ['Предыстория', 'Раса', 'Мировозрение'],
                                          ['Уровень', 'Атрибуты', 'Черты'],
                                          ['Боевые характеристики', 'Кости HP'],
                                          ['Умения и способности', 'Снаряжение'],
                                          ['Прочие владения и языки', 'дохновение'],
                                          ['На главную']],
                                 call_back=[['name_char', 'name_player', 'Class'],
                                          ['Предыстория', 'Раса', 'Мировозрение'],
                                          ['Уровень', 'Атрибуты', 'Черты'],
                                          ['Боевые характеристики', 'Кости HP'],
                                          ['Умения и способности', 'Снаряжение'],
                                          ['Прочие владения и языки', 'дохновение'],
                                          ['start']],
                                 message=call.message)
                              )
    await call.message.delete()
