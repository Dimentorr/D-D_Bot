import asyncio
import logging
from aiogram import Bot, Dispatcher, types

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools

import Forms.register_login.login as login_step
import Forms.register_login.register as reg_step
from States import states_reg_log

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
async def cmd_start(message: types.Message):
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


# Добавляем возможность отмены, если пользователь передумал заполнять
# @dp.message_handler(state='*', types.CallbackQuery.data == 'back')
# async def cancel_handler(state: FSMContext):
#     print('ГАЛЯ')
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     await state.finish()

# @dp.callback_query_handler(lambda c: c.data == 'Registration')
# async def check_data(call: types.CallbackQuery):
#     print(call.data)
# ----------------------------------------------
# ЕСЛИ НУЖНО БУДЕТ В callback_data ДОБАВИТЬ ЧТО_ТО КРОМЕ ПЕРВОГО ТЕГА
# НЕ ЗАБУДЬ ПОМЕНЯТЬ ЛОГИКУ НЕ ТОЛЬКО В СТРОЕНИИ КЛАВИАТУРЫ, НО И
# В ЛОГИКЕ ОТЛАВЛИВАНИЯ ЭТОГО ТЕГА!!
# ----------------------------------------------


@dp.message_handler()
async def check(call: types.CallbackQuery):
    print(call.message)
    print(states_reg_log.StepsReg.NAME)


dp.register_callback_query_handler(login_step.input_login, lambda c: c.data == 'Login')
dp.register_callback_query_handler(login_step.input_password, lambda c: c.data == 'Login_name')
dp.register_callback_query_handler(login_step.check_data, lambda c: c.data == 'Login_password')

dp.register_callback_query_handler(reg_step.input_login,
                                   lambda c: c.data == 'Registration')
dp.register_callback_query_handler(reg_step.input_password,
                                   state=states_reg_log.StepsReg.NAME)
dp.register_callback_query_handler(reg_step.input_repeat_password,
                                   state=states_reg_log.StepsReg.PASSWORD)
dp.register_callback_query_handler(reg_step.check_data,
                                   state=states_reg_log.StepsReg.REPEAT_PASSWORD)

dp.register_callback_query_handler(new_char.menu_create, lambda c: c.data == 'Character')


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())