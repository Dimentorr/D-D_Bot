import asyncio
import logging

from SQL.Tables import MySQLSession, Users, Verify
from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools

from webapp.web_hendlers import web_main
# import Forms.autorization.register as reg_step
from Forms.game_room import main_menu, connect_from, create_new
from Forms.characters import menu_characters, choice_character_for_game
from Forms.verefication import verification
from Forms.supergroup import supergroup_menu
from Forms.pay import donation

from States import (states_connect_to, states_create_group, states_create_character, states_verifiction,
                    states_donate)

from aiogram import F
from aiogram.types import Message

from loader import bot, dp

from aiogram.filters import Command

from aiogram.fsm.context import FSMContext

from asyncio import new_event_loop, set_event_loop

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

set_event_loop(new_event_loop())

BotTools = Tools()
GoogleTools = GoogleTools()


@dp.message(Command('start'))
@dp.callback_query(F.data == 'start')
async def start_bot(message: Message, state: FSMContext):
    user = message.from_user
    if Message != type(message):
        message = message.message
    if message.chat.type == 'private':
        await state.clear()
        with MySQLSession.begin() as session:
            if not session.query(Users).filter_by(id=user.id).first():
                session.add(Users(**{"id": user.id,
                                     "username": user.username,
                                     "firstname": user.first_name}))
            buts = [['Персонажи', 'Компании'],
                    ['Donate']]
            call_backs = [['Character', 'Story'],
                          ['donate']]
            if not session.query(Verify.gmail).filter_by(user_id=user.id).first():
                buts.append('Верификация')
                call_backs.append('verify')
            await message.answer(f'Привет!\n'
                                 f'Этот бот предназначен для:\n'
                                 f'1. хранения листов персонажей игроков\n'
                                 f'2. создания мастером игры групп для общения с игроками\n'
                                 f'(там же все участники компании смогут получить права доступа для '
                                 f'просмотра листов персонажей друг-друга)\n'
                                 f'3. Некоторые функции со временем также появятся (например:'
                                 f' в планах добавить возможность установить время для игры, по которому '
                                 f'бот в личные сообщения будет периодически напоминать об предстоящей игре)\n\n'
                                 f'P.S. По поводу новых функций бота можно написать сюда - @lie_of_life\n\n'
                                 f'P.S.S. Так же вы можете поддержать меня и помочь развитию проекта перейдя по '
                                 f'кнопке "Donate"\n\n'
                                 f'Пожалуйста, выберите интерисующий вас пункт',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=buts,
                                                                                    call_back=call_backs))
        try:
            await message.delete()
        except:
            ...


@dp.message(Command('id'))
async def id_chat(message: Message):
    print(message)
    await message.answer(f"{message.chat.id}")

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

dp.callback_query.register(donation.info, F.data == 'donate')
dp.callback_query.register(donation.input_cost, F.data == 'get_info')
dp.message.register(donation.check_data, states_donate.StepsDonate.cost)
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
dp.callback_query.register(choice_character_for_game.character_choice, F.data.startswith('choice_group-'))
dp.callback_query.register(choice_character_for_game.save_choice, F.data.startswith('choice_character-'))
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------FUNC FOR GROUP-----------------------------------------------------------
dp.message.register(supergroup_menu.group_menu_mess, F.text == '!menu')
dp.callback_query.register(supergroup_menu.group_menu_call, F.data == 'supergroup-menu')
dp.callback_query.register(supergroup_menu.start_get_permissions, F.data == 'supergroup-get_permissions')
dp.callback_query.register(supergroup_menu.get_permissions_list_with_players_and_links_on_characters,
                           F.data.startswith('choice_player-'))
dp.callback_query.register(supergroup_menu.supergroup_check_list_characters,
                           F.data.startswith('supergroup-list_characters'))
# ----------------------------------------------------------------------------------------------------------------------
# dp.message.register(web_main.start_web_app, Command('web_start'))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print('Запускаю шайтан-машину!')
    asyncio.run(dp.start_polling(bot, skip_updates=True))
