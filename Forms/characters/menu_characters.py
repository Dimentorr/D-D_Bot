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


BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def menu_characters(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Создать нового', 'Список существующих'],
                                          ['На главную']],
                                 call_back=[['new_character', 'list_characters'],
                                            ['start']],
                                 message=call.message)
                              )
    await call.answer()
    await call.message.delete()


async def list_characters(call: types.CallbackQuery):
    # test
    ids = con.work_with_MySQL(f'SELECT id FROM character_list WHERE user_id='
                              f'(SELECT id FROM users WHERE user_id="{call.from_user.id}")')[0]
    if len(ids) <= 0:
        await call.message.answer(f'У вас ещё нет созданных персонажей!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=[['Создать персонажа', 'Назад'],
                                               ['На главную']],
                                      call_back=[['new_character', 'Character'],
                                                 ['start']],
                                      message=call.message)
                                  )
    elif len(ids) > 6:
        pass
    else:
        buttons, tags = list(), list()
        for i in range(ids):
            # buttons.append([con.work_with_MySQL(f'SELECT')])
            pass

    await call.message.answer(f'')
