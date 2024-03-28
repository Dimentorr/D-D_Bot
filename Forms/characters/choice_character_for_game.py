from aiogram import types
from aiogram.dispatcher import FSMContext
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from States import states_choice_character

BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def group_choice(call: types.CallbackQuery):
    # create_temp_table = 'CREATE TEMPORARY TABLE user_and_group AS SELECT '
    # insert_data_in_temp_table = ()
    # ------------------------------------------------------------------------------------------------
    # user_id = con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = "{call.from_user.id}"')[0][0]
    # print(user_id)
    # ИЗМЕНИТЬ MySQLTools для работы с запросами, которые возвращают таблицы
    # ИЗМЕНИТЬ ЗАПРОС НА TEMPORARY TABLE
    query_create_temp = (f'CREATE TABLE user_and_group AS SELECT '
                         f'game_stories.name_story as story, '
                         f'game_stories.id as story_id, '
                         f'players_stories.player_id '
                         f'FROM '
                         f'game_stories '
                         f'JOIN players_stories '
                         f'ON game_stories.id=players_stories.story_id;')

    query_find = (f'SELECT story, story_id FROM user_and_group '
                  f'WHERE player_id=(SELECT id FROM users WHERE user_id = {call.from_user.id});')
    query_drop_temp_table = f'DROP TABLE user_and_group;'

    con.work_with_MySQL(query_create_temp)
    names_id = con.work_with_MySQL(query_find)
    con.work_with_MySQL(query_drop_temp_table)

    name_buttons = [f'{i[0]}:{i[1]}' for i in names_id]

    if name_buttons:
        await states_choice_character.StepsChoice.group.set()
        await call.message.answer(f'Пожалуйста выберите интерисующую вас компанию:',
                                  reply_markup=BotTools.construction_inline_keyboard_for_choice(
                                      name_buttons=name_buttons, start_cd='choice_group'))
    else:
        await call.message.answer(f'Вы пока не являетесь игроком ни в одной известной мне компании!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=['Назад'],
                                      call_back=['start']
                                      ))
    await call.answer()
    await call.message.delete()


async def character_choice(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['group'] = call.data
    first_check = con.work_with_MySQL(f'SELECT name_character, id FROM characters_list WHERE user_id = ('
                                           f'SELECT id FROM users WHERE user_id = {call.from_user.id})')
    if first_check:
        id_user = con.work_with_MySQL(f'SELECT id FROM users WHERE user_id = {call.from_user.id}')[0][0]
        names_and_id = con.work_with_MySQL(f'SELECT name_character, id '
                                           f'FROM characters_list WHERE user_id = {id_user} '
                                           f'AND characters_list.id NOT IN ('
                                           f'SELECT selected_characters.character_id FROM selected_characters '
                                           f'WHERE selected_characters.player_id = {id_user});')
        if names_and_id:
            name_buttons = [f'{i[0]}:{i[1]}' for i in names_and_id]
            check_selected_character = con.work_with_MySQL(f'SELECT character_id FROM selected_characters '
                                   f'WHERE story_id = {data["group"].split(":")[1]};')
            if check_selected_character:
                name_select_character = con.work_with_MySQL(f'SELECT name_character FROM characters_list '
                                                            f'WHERE id = {check_selected_character[0][0]};')[0][0]
                message = (f'!!!ВЫ УЖЕ ВЫБИРАЛИ ДЛЯ ЭТОЙ КОМПАНИИ ПЕРСОНАЖА!!!\n\n'
                           f'КОМПАНИЯ - <|{data["group"].split("-")[1].split(":")[0]}|>\n'
                           f'ВЫБРАННЫЙ ПЕРСОНАЖ - <|{name_select_character}|>\n\n'
                           f'ВЫ МОЖЕТЕ ПРОДОЛЖИТЬ ПРИВЯЗКУ ПЕРСОНАЖА, '
                           f'НО В ЭТОМ СЛУЧАИ УЖЕ ВЫБРАННЫЙ ПЕРСОНАЖ БУДЕТ ОТВЯЗАН ОТ ВЫБРАННОЙ КОМПАНИИ\n\n'
                           f'Если вы осознано хотите заменить персонажа для выбранной компании - выберите персонажа:')
            else:
                message = f'Выберите персонажа:'
            await states_choice_character.StepsChoice.next()
            await call.message.answer(message,
                                      reply_markup=BotTools.construction_inline_keyboard_for_choice(
                                          name_buttons=name_buttons, start_cd='choice_character'))
        else:
            await state.finish()
            await call.message.answer(f'Все ваши персонажи уже распределены по компаниям!\n\n'
                                      f'Создайте нового персонажа для этой игры или отвяжите уже существующего',
                                      reply_markup=BotTools.construction_inline_keyboard(
                                          buttons=[['Создать персонажа'], ['Назад']],
                                          call_back=[['new_character'], ['start']]
                                      ))
    else:
        await state.finish()
        await call.message.answer(f'У вас пока что нет созданных персонажей!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=[['Создать персонажа'], ['Назад']],
                                      call_back=[['new_character'], ['start']]
                                  ))
    await call.answer()
    await call.message.delete()

async def save_choice(call: types.CallbackQuery, state: FSMContext):
    print(1)
    async with state.proxy() as data:
        data['character'] = call.data
    print(data['character'])
    print(data["group"])
    selected_character = con.work_with_MySQL(f'SELECT character_id FROM selected_characters '
                                             f'WHERE story_id = {data["group"].split(":")[1]};')
    print(selected_character)
    character_name_id = data["character"].split("-")[1].split(":")
    print(character_name_id)
    story_name_id = data["group"].split("-")[1].split(":")
    print(story_name_id)
    if selected_character:
        print('update')
        con.work_with_MySQL(f'UPDATE selected_characters '
                            f'SET character_id = {character_name_id[1]} '
                            f'WHERE character_id = {selected_character[0][0]}')
    else:
        print('insert')
        con.work_with_MySQL(f'INSERT INTO selected_characters (story_id, character_id, player_id)'
                            f'VALUES({story_name_id[1]}, {character_name_id[1]}, '
                            f'(SELECT id FROM users WHERE user_id = {call.from_user.id}))')
        print('keyboard')
    await call.message.answer(f'Ваш персонаж - <|{character_name_id[0]}|>,'
                              f' теперь привязан к компании - <|{story_name_id[0]}|>!',
                              reply_markup=BotTools.construction_inline_keyboard(
                                  buttons=['Назад'],
                                  call_back=['start']
                              ))
    await call.answer()
    await call.message.delete()
    await state.finish()
