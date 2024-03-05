from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools

import Forms.register_login.login as login_step
import Forms.register_login.register as reg_step
from Forms.game_room import main_menu, connect_from, create_new
from Forms.characters import menu_characters, create_new_character

from States import states_reg_log, states_connect_to, states_create_group

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor

from aiogram.dispatcher import FSMContext

from aiogram.utils.callback_data import CallbackData

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from SQL import users, characters_list, game_story

from asyncio import new_event_loop, set_event_loop
set_event_loop(new_event_loop())


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


@dp.callback_query_handler(lambda c: c.data == 'start', state='*')
async def start_bot(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {call.from_user.id}'):
        await call.message.answer(f'Добро пожаловать в D&D бота!\n'
                                  f'Пожалуйста, выберите интерисующий вас пункт',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=['Персонажи', 'Компании'],
                                      call_back=['Character', 'Story'],
                                      message=call.message))
    else:
        await call.message.answer('Зарегистрируйтесь для продолжения работы в боте',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=['Регистрация'],
                                      call_back=['Registration'],
                                      message=call.message))
    await call.message.delete()


@dp.message_handler(commands=['start'])
async def start_bot(message: Message, state: FSMContext):
    await state.finish()
    if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {message.from_user.id}'):
        await message.answer(f'Добро пожаловать в D&D бота!\n'
                             f'Пожалуйста, выберите интерисующий вас пункт',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Персонажи', 'Компании'],
                                 call_back=['Character', 'Story'],
                                 message=message))
    else:
        await message.answer('Зарегистрируйтесь для продолжения работы в боте',
                             reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=['Регистрация'],
                                 call_back=['Registration'],
                                 message=message))


@dp.message_handler(commands=['id'])
async def id_chat(message: Message):
    await message.answer(f"{message.chat.id}")


dp.register_callback_query_handler(reg_step.input_login,
                                   (lambda c: c.data == 'Registration'), state='*')
dp.register_message_handler(reg_step.input_password, state=states_reg_log.StepsReg.name)
dp.register_message_handler(reg_step.input_repeat_password, state=states_reg_log.StepsReg.password)
dp.register_message_handler(reg_step.check_data, state=states_reg_log.StepsReg.repeat_password)


dp.register_callback_query_handler(login_step.input_login,
                                   (lambda c: c.data == 'Login'), state='*')
dp.register_message_handler(login_step.input_password, state=states_reg_log.StepsLogin.name)
dp.register_message_handler(login_step.check_data, state=states_reg_log.StepsLogin.password)


dp.register_callback_query_handler(main_menu.first_menu_game_function,
                                   lambda c: c.data == 'Story', state='*')

dp.register_callback_query_handler(connect_from.linc_group_id,
                                   lambda c: c.data == 'connect_to', state='*')
dp.register_message_handler(connect_from.linc_group_password, state=states_connect_to.StepsConnectTo.id)
dp.register_message_handler(connect_from.linc_group_check, state=states_connect_to.StepsConnectTo.password)


dp.register_callback_query_handler(create_new.create_group_name,
                                   lambda c: c.data == 'create_new_game', state='*')
dp.register_message_handler(create_new.create_group_password, state=states_create_group.StepsCreate.name_group)
dp.register_message_handler(create_new.create_group_repeat_password, state=states_create_group.StepsCreate.password)
dp.register_message_handler(create_new.create_group_check, state=states_create_group.StepsCreate.repeat_password)


dp.register_callback_query_handler(menu_characters.menu_characters,
                                   lambda c: c.data == 'Character', state='*')
dp.register_callback_query_handler(create_new_character.menu_create,
                                   lambda c: c.data == 'new_character', state='*')

if __name__ == "__main__":
    users.create_table()
    characters_list.create_table()
    game_story.create_table()

    executor.start_polling(dp, skip_updates=True)
