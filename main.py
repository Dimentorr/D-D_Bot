import asyncio
import logging

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools

import Forms.register_login.login as login_step
import Forms.register_login.register as reg_step
from States import states_reg_log
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor

from aiogram.dispatcher import FSMContext

import Forms.characters.create_new_character as new_char

from aiogram.utils.callback_data import CallbackData

from aiogram.contrib.fsm_storage.memory import MemoryStorage


cd_list = CallbackData('teg_step')

BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
bot = Bot(token=env.read_json_data('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


@dp.message_handler(commands=['start'])
async def start_bot(message: Message, state: FSMContext):
    await state.finish()
    if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {message.from_user.id}'):
        del_keyboard = types.ReplyKeyboardRemove()
        await message.answer('Добро пожаловать в D&D бота!', reply_markup=del_keyboard)
        await message.answer('Пожалуйста, выберите интерисующий вас пункт',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Персонажи', 'Компании'],
                                 call_back=['Character', 'Story'],
                                 message=message))
    else:
        await message.answer('Зарегистрируйтесь или авторизуйтесь',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Регистрация', 'Авторизация'],
                                 call_back=['Registration', 'Login'],
                                 message=message))


dp.register_callback_query_handler(reg_step.input_login,
                                   (lambda c: c.data == 'Registration'), state='*')
dp.register_message_handler(reg_step.input_password, state=states_reg_log.StepsReg.name)
dp.register_message_handler(reg_step.input_repeat_password, state=states_reg_log.StepsReg.password)
dp.register_message_handler(reg_step.check_data, state=states_reg_log.StepsReg.repeat_password)


dp.register_callback_query_handler(login_step.input_login,
                                   (lambda c: c.data == 'Login'), state='*')
dp.register_message_handler(login_step.input_password, state=states_reg_log.StepsLogin.name)
dp.register_message_handler(login_step.check_data, state=states_reg_log.StepsLogin.password)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
