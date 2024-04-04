import asyncio

from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from Tools.SQLiteTools import Connection as LiteConnection

import Forms.autorization.register as reg_step
from Forms.game_room import main_menu, connect_from, create_new
from Forms.characters import menu_characters, choice_character_for_game
from Forms.verefication import verification
from Forms.supergroup import supergroup_menu

from States import states_reg_log, states_connect_to, states_create_group, states_create_character, states_verifiction

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery

from aiogram.filters import Command

from aiogram.fsm.context import FSMContext

from SQL import users, characters_list, game_story, verify, selected_characters

from asyncio import new_event_loop, set_event_loop

from aiogram.client.session.aiohttp import AiohttpSession


set_event_loop(new_event_loop())

BotTools = Tools()
GoogleTools = GoogleTools()
env = CatalogJson(name='file/json/environment.json')
# session = AiohttpSession(proxy='http://proxy.server:3128')
# bot = Bot(token=env.read_json_data('TOKEN'), session=session)
bot = Bot(token=env.read_json_data('TOKEN'))
dp = Dispatcher()


con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))
l_con = LiteConnection(path='file/db/bot_base.db')


@dp.callback_query(F.data == 'start')
async def start_bot(call: CallbackQuery, state: FSMContext):
    if call.message.chat.type == 'private':
        await state.clear()
        # if con.work_with_MySQL([f'SELECT id FROM users WHERE user_id = {call.from_user.id}']):
        if l_con.work_with_SQLite([f'SELECT id FROM users WHERE user_id = {call.from_user.id}']):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = ([f'SELECT gmail FROM verify '
                          f'WHERE user_id = '
                          f'(SELECT id FROM users WHERE user_id = {call.from_user.id})'])
            # if not con.work_with_MySQL(query_log):
            if not l_con.work_with_SQLite(query_log):
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


@dp.message(Command('start'))
async def start_bot(message: Message, state: FSMContext):
    if message.chat.type == 'private':
        await state.clear()
        await message.answer('Этот бот предназначен для:\n'
                             '1. хранения листов персонажей игроков\n'
                             '2. создания мастером игры групп для общения с игроками\n'
                             '(там же все участники компании смогут получить права доступа для '
                             'просмотра листов персонажей друг-друга)\n'
                             '3. Некоторые функции со временем также появятся (например:'
                             ' в планах добавить возможность установить время для игры, по которому '
                             'бот в личные сообщения будет периодически напоминать об предстоящей игре)'
                             '\n\n'
                             'P.S. По поводу новых функций бота можно написать сюда - @lie_of_life')
        # if con.work_with_MySQL([f'SELECT id FROM users WHERE user_id = {message.from_user.id}']):
        if l_con.work_with_SQLite([f'SELECT id FROM users WHERE user_id = {message.from_user.id}']):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = ([f'SELECT gmail FROM verify '
                          f'WHERE user_id = '
                          f'(SELECT id FROM users WHERE user_id = {message.from_user.id})'])
            # if not con.work_with_MySQL(query_log):
            if not l_con.work_with_SQLite(query_log):
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


@dp.message(Command('id'))
async def id_chat(message: Message):
    print(message)
    await message.answer(f"{message.chat.id}")

# --------------------------------------------STEPS REGISTRATION--------------------------------------------------------
dp.callback_query.register(reg_step.input_login, (F.data == 'Registration'))
dp.message.register(reg_step.input_password, states_reg_log.StepsReg.name)
dp.message.register(reg_step.input_repeat_password, states_reg_log.StepsReg.password)
dp.message.register(reg_step.check_data, states_reg_log.StepsReg.repeat_password)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------STEPS VERIFICATION--------------------------------------------------------
dp.callback_query.register(verification.start_verify, (F.data == 'verify'))
dp.callback_query.register(verification.input_gmail, (F.data == 'input_gmail'))
dp.message.register(verification.input_code, states_verifiction.StepsVerification.gmail)
dp.message.register(verification.check_data, states_verifiction.StepsVerification.code)
dp.callback_query.register(verification.repeat_generate_code, (F.data == 'repeat_generate_code_verify'))
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------MAIN MENU'S BOT-----------------------------------------------------------
dp.callback_query.register(main_menu.first_menu_game_function, F.data == 'Story')

dp.callback_query.register(connect_from.linc_group_id, F.data == 'connect_to')
dp.message.register(connect_from.linc_group_password, states_connect_to.StepsConnectTo.id)
dp.message.register(connect_from.linc_group_check, states_connect_to.StepsConnectTo.password)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------STEPS CREATE GAME---------------------------------------------------------
dp.callback_query.register(create_new.create_group_name, F.data == 'create_new_game')
dp.message.register(create_new.create_group_password, states_create_group.StepsCreate.name_group)
dp.message.register(create_new.create_group_repeat_password, states_create_group.StepsCreate.password)
dp.message.register(create_new.create_group_check, states_create_group.StepsCreate.repeat_password)
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------STEPS CHARACTERS(LIST/CREATE/CHOICE_FOR_GAME)-------------------------------------------
dp.callback_query.register(menu_characters.menu_characters, F.data == 'Character')
dp.callback_query.register(menu_characters.new_sheet_character, F.data == 'new_character')
dp.message.register(menu_characters.create_sheet_character, states_create_character.StepsCreateCharacter.name)
dp.callback_query.register(menu_characters.list_characters, F.data == 'list_characters')
dp.callback_query.register(choice_character_for_game.group_choice, F.data == 'choice_characters')
dp.callback_query.register(choice_character_for_game.character_choice, lambda c: 'choice_group-' in c.data)
dp.callback_query.register(choice_character_for_game.save_choice, lambda c: 'choice_character-' in c.data)
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------FUNC FOR GROUP-----------------------------------------------------------
dp.message.register(supergroup_menu.group_menu_mess, F.text == '!menu')
dp.callback_query.register(supergroup_menu.group_menu_call, F.data == 'supergroup-menu')
dp.callback_query.register(supergroup_menu.start_get_permissions, F.data == 'supergroup-get_permissions')
dp.callback_query.register(supergroup_menu.get_permissions_list_with_players_and_links_on_characters,
                           lambda c: 'choice_player-' in c.data)
dp.callback_query.register(supergroup_menu.supergroup_check_list_characters,
                           lambda c: 'supergroup-list_characters' in c.data)
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    if int(env.read_json_data('create_table')):
        users.create_table(is_mysql=False)
        verify.create_table(is_mysql=False)
        characters_list.create_table(is_mysql=False)
        game_story.create_table(is_mysql=False)
        selected_characters.create_table(is_mysql=False)
    print('Запускаю шайтан-машину!')
    asyncio.run(dp.start_polling(bot, skip_updates=True))
