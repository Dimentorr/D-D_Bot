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


data = dict()
BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))