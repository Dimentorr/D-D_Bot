from aiogram import types
from aiogram.fsm.context import FSMContext

from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from SQL.Tables import MySQLSession, Characters, Users, GameStories, PlayersStories, SelectedCharacters, Verify
from sqlalchemy import and_

from dotenv import load_dotenv

GoogleTools = GoogleTools()
load_dotenv(dotenv_path='.env')
BotTools = Tools()


async def group_menu_call(call: types.CallbackQuery):
    if call.message.chat.type == 'supergroup':
        from main import bot
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Меню супергруппы:',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=[['Список персонажей'], ['Получить права просмотра']],
                                   cd=[['list_characters'], ['get_permissions']]
                               ))
        await call.message.delete()


async def group_menu_mess(message: types.Message):
    if message.chat.type == 'supergroup':
        from main import bot
        await bot.send_message(chat_id=message.chat.id,
                               text='Меню супергруппы:',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=[['Список персонажей'], ['Получить права просмотра']],
                                   cd=[['list_characters'], ['get_permissions']]
                               ))


def check_verify(user_id: str | int):
    with MySQLSession.begin() as session:
        if mail := session.query(Verify.gmail).filter_by(user_id=user_id).first():
            return mail[0]
        else:
            return None


async def start_get_permissions(call: types.CallbackQuery):
    from main import bot
    group_id = call.message.chat.id
    with MySQLSession.begin() as session:
        if not session.query(GameStories.name).filter_by(id=group_id).first():
            print(f'group {group_id} not found!')
            await bot.send_message(chat_id=call.message.chat.id,
                                   text='Компания не найдена в моей базе данных!',
                                   reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                       name_buttons=['Назад'],
                                       cd=['menu']
                                   ))
            await call.message.delete()
            return 0
        else:
            ids_users = [i[0] for i in session.query(PlayersStories.player_id).filter(
                PlayersStories.story_id == group_id).all()]
            if len(ids_users) == 0:
                await bot.send_message(chat_id=call.message.chat.id,
                                       text='В данной компании ещё нет игроков!',
                                       reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                           name_buttons=['Назад'],
                                           cd=['menu']
                                       ))
                await call.message.delete()
                return 0

            data_buttons = []
            print(ids_users)
            print(len(ids_users))
            for player_id in ids_users:
                player_name = session.query(Users.firstname).filter(Users.id == player_id).first()[0]
                if user_id := session.query(SelectedCharacters.player_id).filter(
                    and_(SelectedCharacters.story_id == group_id,
                         SelectedCharacters.player_id == player_id,
                         )
                ).all():
                    print(f'привязал персонажа - {player_name}')
                    data_buttons.append(f'{player_name}:{user_id[0][0]}')
                else:
                    print(f'не привязал персонажа - {player_name}')
                    data_buttons.append(f'{player_name}:-1')
            await bot.send_message(chat_id=call.message.chat.id,
                                   text='Вот список всех Игроков, выберите того, доступ к чьему листу вы хотите получить:',
                                   reply_markup=BotTools.construction_inline_keyboard_for_choice(
                                       name_buttons=data_buttons,
                                       start_cd='choice_player',
                                       private=False))


async def get_permissions_list_with_players_and_links_on_characters(call: types.CallbackQuery):
    from main import bot
    user_id = call.from_user.id
    mail_user = check_verify(user_id)
    if not mail_user:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Для этого тебе необходимо пройти верефикацию!\n'
                                    'Для этого перейдите в личную беседу со мной |@PSMagicBot|'
                                    ' и в основном меню выберите |Верификация|',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=['Назад'],
                                   cd=['menu']
                               ))
        await call.message.delete()
        return 0
    else:
        chat_id = call.message.chat.id
        with MySQLSession.begin() as session:
            # owner_character = session.query(Users.id).filter
            print(call.data)
            player_id = call.data.split(':')[1]
            if character_id := session.query(SelectedCharacters.player_id, SelectedCharacters.character_id).filter(
                and_(SelectedCharacters.story_id == call.message.chat.id,
                     SelectedCharacters.player_id == player_id)
            ).all():
                GoogleTools.get_permissions(file_id=character_id[0][1],
                                            email=mail_user)
                name_character_user_id = session.query(Characters.name, Characters.user_id).filter(
                    Characters.id == character_id[0][1]).first()
                name_user = session.query(Users.firstname).filter(Users.id == user_id).first()[0]
                await bot.send_message(chat_id=chat_id,
                                       text=f'Игрок '
                                            f'|{name_user}| получил права на просмотр листа '
                                            f'персонажа - |{name_character_user_id[0]}|',
                                       reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                           name_buttons=['Назад'],
                                           cd=['menu']
                                       ))
            else:
                await bot.send_message(chat_id=chat_id,
                                       text=f'Игрок '
                                            f'|{call.data.split("-")[1].split(":")[0]}| '
                                            f'ещё не привязал своего персонажа к игре!',
                                       reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                           name_buttons=['Назад'],
                                           cd=['menu']))
        await call.message.delete()


async def find_list(group_id: str):
    characters_name_link = []
    with MySQLSession.begin() as session:
        characters_ids = session.query(SelectedCharacters.character_id).filter(
            SelectedCharacters.story_id == group_id).all()
        for i in characters_ids:
            character = session.query(Characters.name, Characters.link).filter(Characters.id == i[0]).first()
            characters_name_link.append([character[0], character[1]])
        return characters_name_link


async def supergroup_check_list_characters(call: types.CallbackQuery):
    from main import bot
    with MySQLSession.begin() as session:
        if group_id := session.query(GameStories.id).filter(GameStories.id == call.message.chat.id).first():
            if session.query(PlayersStories.id).filter(PlayersStories.story_id == group_id[0]).all():
                list_characters = await find_list(group_id[0])
                if list_characters:
                    names, links = [], []
                    for i in list_characters:
                        names.append(i[0])
                        links.append(i[1])
                    await bot.send_message(chat_id=group_id[0],
                                           text='Вот список всех Персонажей, выберите того, чей лист вы хотите посмотреть',
                                           reply_markup=BotTools.construction_inline_keyboard_with_link(
                                               list_name=names,
                                               list_link=links,
                                               private=False))
                else:
                    await bot.send_message(chat_id=group_id[0],
                                           text='Никто из игроков ещё не привязал своего персонажа к этой игре!',
                                           reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                               name_buttons=['Назад'],
                                               cd=['menu']
                                           ))
                await call.message.delete()
            else:
                await bot.send_message(chat_id=group_id[0],
                                       text='В данной компании ещё нет игроков!',
                                       reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                           name_buttons=['Назад'],
                                           cd=['menu']
                                       ))
                await call.message.delete()
                return 0
        else:
            print(f'supergroup start_get_permissions - group not found')
            await bot.send_message(chat_id=call.message.chat.id,
                                   text='Компания не найдена в моей базе данных!',
                                   reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                       name_buttons=['Назад'],
                                       cd=['menu']
                                   ))
            await call.message.delete()
            return 0
