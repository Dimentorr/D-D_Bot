from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools

import Forms.autorization.login as login_step
import Forms.autorization.register as reg_step
from Forms.game_room import main_menu, connect_from, create_new
from Forms.characters import menu_characters, choice_character_for_game
from Forms.verefication import verification
from Forms.supergroup import supergroup_menu

from States import states_reg_log, states_connect_to, states_create_group, states_create_character, states_verifiction

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils import executor

from aiogram.dispatcher import FSMContext

from aiogram.utils.callback_data import CallbackData

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from SQL import users, characters_list, game_story, verify, selected_characters

from asyncio import new_event_loop, set_event_loop


set_event_loop(new_event_loop())

cd_list = CallbackData('teg_step')

BotTools = Tools()
GoogleTools = GoogleTools()
env = CatalogJson(name='file/json/environment.json')
bot = Bot(token=env.read_json_data('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


@dp.callback_query_handler(lambda c: c.data == 'start', state='*')
async def start_bot(call: CallbackQuery, state: FSMContext):
    if call.message.chat.type == 'private':
        await state.finish()
        if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {call.from_user.id}'):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = (f'SELECT gmail FROM verify '
                         f'WHERE user_id = '
                         f'(SELECT id FROM users WHERE user_id = {call.from_user.id})')
            if not con.work_with_MySQL(query_log):
                buts.append('Верификация')
                call_backs.append('verify')
            await call.message.answer(f'Добро пожаловать в D&D бота!\n'
                                      f'Пожалуйста, выберите интерисующий вас пункт',
                                      reply_markup=BotTools.construction_inline_keyboard(buttons=buts,
                                                                                         call_back=call_backs))
        else:
            await call.message.answer('Зарегистрируйтесь для продолжения работы в боте',
                                      reply_markup=BotTools.construction_inline_keyboard(buttons=['Регистрация'],
                                                                                         call_back=['Registration']))
        await call.message.delete()


@dp.message_handler(commands=['start'])
async def start_bot(message: Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.finish()
        if con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {message.from_user.id}'):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = (f'SELECT gmail FROM verify '
                         f'WHERE user_id = '
                         f'(SELECT id FROM users WHERE user_id = {message.from_user.id})')
            if not con.work_with_MySQL(query_log):
                buts.append('Верификация')
                call_backs.append('verify')
            await message.answer(f'Добро пожаловать в D&D бота!\n'
                                 f'Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=buts,
                                                                                    call_back=call_backs))
        else:
            await message.answer('Зарегистрируйтесь для продолжения работы в боте',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['Регистрация'],
                                                                                    call_back=['Registration']))


@dp.message_handler(commands=['id'])
async def id_chat(message: Message):
    print(message)
    await message.answer(f"{message.chat.id}")

# --------------------------------------------STEPS REGISTRATION--------------------------------------------------------
dp.register_callback_query_handler(reg_step.input_login,
                                   (lambda c: c.data == 'Registration'), state='*')
dp.register_message_handler(reg_step.input_password, state=states_reg_log.StepsReg.name)
dp.register_message_handler(reg_step.input_repeat_password, state=states_reg_log.StepsReg.password)
dp.register_message_handler(reg_step.check_data, state=states_reg_log.StepsReg.repeat_password)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------STEPS LOGIN---------------------------------------------------------------
dp.register_callback_query_handler(login_step.input_login,
                                   (lambda c: c.data == 'Login'), state='*')
dp.register_message_handler(login_step.input_password, state=states_reg_log.StepsLogin.name)
dp.register_message_handler(login_step.check_data, state=states_reg_log.StepsLogin.password)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------STEPS VERIFICATION--------------------------------------------------------
dp.register_callback_query_handler(verification.start_verify,
                                   (lambda c: c.data == 'verify'), state='*')
dp.register_callback_query_handler(verification.input_gmail,
                                   (lambda c: c.data == 'input_gmail'), state='*')
dp.register_message_handler(verification.input_code, state=states_verifiction.StepsVerification.gmail)
dp.register_message_handler(verification.check_data, state=states_verifiction.StepsVerification.code)
dp.register_callback_query_handler(verification.repeat_generate_code,
                                   (lambda c: c.data == 'repeat_generate_code_verify'), state='*')
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------MAIN MENU'S BOT-----------------------------------------------------------
dp.register_callback_query_handler(main_menu.first_menu_game_function,
                                   lambda c: c.data == 'Story', state='*')

dp.register_callback_query_handler(connect_from.linc_group_id,
                                   lambda c: c.data == 'connect_to', state='*')
dp.register_message_handler(connect_from.linc_group_password, state=states_connect_to.StepsConnectTo.id)
dp.register_message_handler(connect_from.linc_group_check, state=states_connect_to.StepsConnectTo.password)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------STEPS CREATE GAME---------------------------------------------------------
dp.register_callback_query_handler(create_new.create_group_name,
                                   lambda c: c.data == 'create_new_game', state='*')
dp.register_message_handler(create_new.create_group_password, state=states_create_group.StepsCreate.name_group)
dp.register_message_handler(create_new.create_group_repeat_password, state=states_create_group.StepsCreate.password)
dp.register_message_handler(create_new.create_group_check, state=states_create_group.StepsCreate.repeat_password)
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------STEPS CHARACTERS(LIST/CREATE/CHOICE_FOR_GAME)-------------------------------------------
dp.register_callback_query_handler(menu_characters.menu_characters,
                                   lambda c: c.data == 'Character', state='*')
dp.register_callback_query_handler(menu_characters.new_sheet_character,
                                   lambda c: c.data == 'new_character', state='*')
dp.register_message_handler(menu_characters.create_sheet_character,
                            state=states_create_character.StepsCreateCharacter.name)
dp.register_callback_query_handler(menu_characters.list_characters,
                                   lambda c: c.data == 'list_characters', state='*')
dp.register_callback_query_handler(choice_character_for_game.group_choice,
                                   lambda c: c.data == 'choice_characters', state='*')

dp.register_callback_query_handler(choice_character_for_game.character_choice,
                                   lambda c: 'choice_group-' in c.data, state='*')
dp.register_callback_query_handler(choice_character_for_game.save_choice,
                                   lambda c: 'choice_character-' in c.data, state='*')
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------FUNC FOR GROUP-----------------------------------------------------------
dp.register_message_handler(supergroup_menu.group_menu_mess,
                            lambda m: m.text == '!menu', state='*')
dp.register_callback_query_handler(supergroup_menu.group_menu_call,
                                   lambda c: c.data == 'supergroup-menu', state='*')
dp.register_callback_query_handler(supergroup_menu.start_get_permissions,
                                   lambda c: c.data == 'supergroup-get_permissions', state='*')
dp.register_callback_query_handler(supergroup_menu.get_permissions_list_with_players_and_links_on_characters,
                                   lambda c: 'choice_player-' in c.data, state='*')
dp.register_callback_query_handler(supergroup_menu.supergroup_check_list_characters,
                                   lambda c: c.data == 'supergroup-list_characters', state='*')
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    if int(env.read_json_data('create_table')):
        users.create_table()
        verify.create_table()
        characters_list.create_table()
        game_story.create_table()
        selected_characters.create_table()
    executor.start_polling(dp, skip_updates=True)
