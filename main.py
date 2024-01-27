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

import Forms.register_login.login as login_step
import Forms.register_login.register as reg_step

BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=env.read_json_data('TOKEN'))
dp = Dispatcher()

con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {message.from_user.id}'):
        await message.answer('hi')
    else:
        await message.answer('Зарегистрируйтесь или авторизуйтесь',
                             reply_markup=BotTools.construction_keyboard(
                                 buttons=['Регистрация', 'Авторизация'],
                                 call_back=['Reg', 'Log']))


dp.message.register(login_step.input_login, (F.text == 'Авторизация') | (F.text == 'Попробовать сново'))
dp.message.register(login_step.input_password, login_step.states_reg_log.StepsLogin.NAME)
dp.message.register(login_step.check_data, login_step.states_reg_log.StepsLogin.PASSWORD)

dp.message.register(reg_step.input_login, F.text == 'Регистрация')
dp.message.register(reg_step.input_password, reg_step.states_reg_log.StepsReg.NAME)
dp.message.register(reg_step.input_repeat_password, reg_step.states_reg_log.StepsReg.PASSWORD)
dp.message.register(reg_step.check_data, reg_step.states_reg_log.StepsReg.REPEAT_PASSWORD)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())