from aiogram import types

from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from Tools.MySqlTools import Connection
from Tools.SQLiteTools import Connection as LiteConnection

import os
from dotenv import load_dotenv

GoogleTools = GoogleTools()
load_dotenv(dotenv_path='.env')
BotTools = Tools()
# con = Connection(host=env.read_json_data('DB_host'),
#                  port=env.read_json_data('DB_port'),
#                  database_name=env.read_json_data('DB_database'),
#                  user=env.read_json_data('DB_user'),
#                  password=env.read_json_data('DB_password'))
l_con = LiteConnection(path=os.getenv('path_sqlite_db'))


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
    # mail = con.work_with_MySQL([f'Select gmail FROM verify '
    #                             f'WHERE user_id = '
    #                             f'(Select id FROM users '
    #                             f'WHERE user_id = {user_id})'])
    mail = l_con.work_with_SQLite([f'Select gmail FROM verify '
                                   f'WHERE user_id = '
                                   f'(Select id FROM users '
                                   f'WHERE user_id = {user_id})'])
    if mail:
        return mail[0][0]
    else:
        return None


async def start_get_permissions(call: types.CallbackQuery):
    from main import bot
    try:
        # group_id = con.work_with_MySQL(
        # [f'SELECT id FROM game_stories WHERE id_group="{call.message.chat.id}";'])[0][0]
        group_id = l_con.work_with_SQLite(
            [f'SELECT id FROM game_stories WHERE id_group="{call.message.chat.id}";'])[0][0]
    except Exception as err:
        print(f'supergroup start_get_permissions - {err}')
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Компания не найдена в моей базе данных!',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=['Назад'],
                                   cd=['menu']
                               ))
        await call.message.delete()
        return 0
    # ids_users = [i[0] for i in
    #              con.work_with_MySQL([f'SELECT player_id FROM players_stories WHERE story_id={group_id};'])]
    ids_users = [i[0] for i in
                 l_con.work_with_SQLite([f'SELECT player_id FROM players_stories WHERE story_id={group_id};'])]
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
    for player_id in ids_users:
        # character = con.work_with_temporary_on_MySQL([[f'CREATE TEMPORARY TABLE user_character_id AS '
        #                                                f'SELECT users.id as user_id, '
        #                                                f'users.name_user as user, '
        #                                                f'characters_list.id as character_id, '
        #                                                f'selected_characters.story_id as story_id '
        #                                                f'FROM '
        #                                                f'selected_characters '
        #                                                f'INNER JOIN characters_list '
        #                                                f'ON characters_list.id = selected_characters.character_id '
        #                                                f'INNER JOIN users '
        #                                                f'ON users.id = selected_characters.player_id;'],
        #                                               [f'SELECT user, character_id '
        #                                                f'FROM user_character_id '
        #                                                f'WHERE '
        #                                                f'story_id = {group_id} AND user_id = {player_id};']])
        character = l_con.work_with_SQLite([[f'CREATE TEMPORARY TABLE user_character_id AS '
                                                       f'SELECT users.id as user_id, '
                                                       f'users.name_user as user, '
                                                       f'characters_list.id as character_id, '
                                                       f'selected_characters.story_id as story_id '
                                                       f'FROM '
                                                       f'selected_characters '
                                                       f'INNER JOIN characters_list '
                                                       f'ON characters_list.id = selected_characters.character_id '
                                                       f'INNER JOIN users '
                                                       f'ON users.id = selected_characters.player_id;'],
                                                      [f'SELECT user, character_id '
                                                       f'FROM user_character_id '
                                                       f'WHERE '
                                                       f'story_id = {group_id} AND user_id = {player_id};']])
        if character:
            data_buttons.append(f'{character[0][0]}:{character[0][1]}')
        else:
            # name = con.work_with_MySQL([f'SELECT name_user FROM users WHERE id = {player_id};'])[0][0]
            name = l_con.work_with_SQLite([f'SELECT name_user FROM users WHERE id = {player_id};'])[0][0]
            data_buttons.append(f'{name}:{-1}')
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Вот список всех Игроков, выберите того, доступ к чьему листу вы хотите получить:',
                           reply_markup=BotTools.construction_inline_keyboard_for_choice(
                               name_buttons=data_buttons,
                               start_cd='choice_player',
                               private=False))


async def get_permissions_list_with_players_and_links_on_characters(call: types.CallbackQuery):
    from main import bot
    mail_user = check_verify(call.from_user.id)
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
        if int(call.data.split(":")[1]) > 0:
            # GoogleTools.get_permissions(file_id=con.work_with_MySQL([f'SELECT file_id FROM characters_list '
            #                                                         f'WHERE id = {call.data.split(":")[1]}'][0][0]),
            #                             email=mail_user)
            GoogleTools.get_permissions(file_id=l_con.work_with_SQLite([f'SELECT file_id FROM characters_list '
                                                                        f'WHERE id = {call.data.split(":")[1]}'])[0][0],
                                        email=mail_user)
            # name_character = con.work_with_MySQL([f'SELECT name_character FROM characters_list '
            #                                      f'WHERE id = {call.data.split(":")[1]}'])
            name_character = l_con.work_with_SQLite([f'SELECT name_character FROM characters_list '
                                                     f'WHERE id = {call.data.split(":")[1]}'])
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=f'Игрок '
                                        f'|{call.data.split("-")[1].split(":")[0]}| получил права на просмотр листа '
                                        f'персонажа - |{name_character}|',
                                   reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                       name_buttons=['Назад'],
                                       cd=['menu']
                                   ))
        else:
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=f'Игрок '
                                        f'|{call.data.split("-")[1].split(":")[0]}| '
                                        f'ещё не привязал своего персонажа к игре!',
                                   reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                       name_buttons=['Назад'],
                                       cd=['menu']))
        await call.message.delete()


async def find_list(group_id: str):

    # characters_name_link = (
    #     con.work_with_MySQL([f'SELECT name_character, link FROM characters_list '
    #                          f'WHERE id=('
    #                          f'SELECT character_id FROM selected_characters WHERE story_id={group_id}'
    #                          f');']))
    characters_name_link = (
        l_con.work_with_SQLite([[f'CREATE TEMPORARY TABLE characters_id_in_games AS '
                                 f'SELECT '
                                 f'selected_characters.story_id,'
                                 f'selected_characters.character_id, '
                                 f'selected_characters.player_id,'
                                 f'characters_list.name_character,'
                                 f'characters_list.link '
                                 f'FROM '
                                 f'selected_characters '
                                 f'JOIN characters_list '
                                 f'ON selected_characters.character_id = characters_list.id;'],
                               [f'SELECT name_character,link FROM characters_id_in_games '
                                f'WHERE story_id={group_id};']]))

    if len(characters_name_link) == 0:
        return []
    else:
        return characters_name_link


async def supergroup_check_list_characters(call: types.CallbackQuery):
    from main import bot
    try:
        # group_id = con.work_with_MySQL(
    # [f'SELECT id FROM game_stories WHERE id_group="{call.message.chat.id}";'])[0][0]
        group_id = l_con.work_with_SQLite([
            f'SELECT id FROM game_stories WHERE id_group="{call.message.chat.id}";'])[0][0]
    except Exception as err:
        print(f'supergroup start_get_permissions - {err}')
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Компания не найдена в моей базе данных!',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=['Назад'],
                                   cd=['menu']
                               ))
        await call.message.delete()
        return 0
    # ids_users = [i[0] for i in
    #              con.work_with_MySQL([f'SELECT player_id FROM players_stories WHERE story_id={group_id};'])]
    ids_users = [i[0] for i in
                 l_con.work_with_SQLite([f'SELECT player_id FROM players_stories WHERE story_id={group_id};'])]
    if len(ids_users) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='В данной компании ещё нет игроков!',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=['Назад'],
                                   cd=['menu']
                               ))
        await call.message.delete()
        return 0

    list_characters = await find_list(group_id)
    if list_characters:
        names = []
        links = []
        for i in list_characters:
            names.append(i[0])
            links.append(i[1])
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Вот список всех Персонажей, выберите того, чей лист вы хотите посмотреть',
                               reply_markup=BotTools.construction_inline_keyboard_with_link(
                                   list_name=names,
                                   list_link=links,
                                   private=False))
    else:
        await bot.send_message(chat_id=call.message.chat.id,
                               text='Никто из игроков ещё не привязал своего персонажа к этой игре!',
                               reply_markup=BotTools.construction_inline_keyboard_for_supergroup(
                                   name_buttons=['Назад'],
                                   cd=['menu']
                               ))
    await call.message.delete()
