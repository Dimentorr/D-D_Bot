import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.bot import DefaultBotProperties

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

from asyncio import new_event_loop, set_event_loop

from SQL import users, characters_list, game_story, verify, selected_characters

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

set_event_loop(new_event_loop())

BotTools = Tools()
GoogleTools = GoogleTools()

set_event_loop(new_event_loop())
l_con = LiteConnection(path=os.getenv('path_sqlite_db'))
if int(os.getenv('create_table')):
    users.create_table(is_mysql=False)
    verify.create_table(is_mysql=False)
    characters_list.create_table(is_mysql=False)
    game_story.create_table(is_mysql=False)
    selected_characters.create_table(is_mysql=False)
WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 80

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "my-secret"
BASE_WEBHOOK_URL = "https://f703-77-34-2-187.ngrok-free.app"

router = Router()


@router.callback_query(F.data == 'start')
async def start_bot(call: CallbackQuery, state: FSMContext):
    if call.message.chat.type == 'private':
        await state.clear()
        if l_con.work_with_SQLite([f'SELECT id FROM users WHERE user_id = {call.from_user.id}']):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = ([f'SELECT gmail FROM verify '
                          f'WHERE user_id = '
                          f'(SELECT id FROM users WHERE user_id = {call.from_user.id})'])
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


@router.message(Command('start'))
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
        if l_con.work_with_SQLite([f'SELECT id FROM users WHERE user_id = {message.from_user.id}']):
            buts = ['Персонажи', 'Компании']
            call_backs = ['Character', 'Story']
            query_log = ([f'SELECT gmail FROM verify '
                          f'WHERE user_id = '
                          f'(SELECT id FROM users WHERE user_id = {message.from_user.id})'])
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


@router.message(Command('id'))
async def id_chat(message: Message):
    print(message)
    await message.answer(f"{message.chat.id}")


def register_handlers(dp: Dispatcher):
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


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


dp = Dispatcher()
dp.include_router(router)
dp.startup.register(on_startup)
bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

def main() -> None:
    register_handlers(dp)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()