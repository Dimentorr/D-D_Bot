from aiogram import types
from aiogram.fsm.context import FSMContext

from States import states_create_character

from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from Tools.JsonTools import CatalogJson
from Tools.MySqlTools import Connection
from Tools.SQLiteTools import Connection as LiteConnection

import os
from dotenv import load_dotenv

GoogleTools = GoogleTools()

load_dotenv()

BotTools = Tools()
# con = Connection(host=env.read_json_data('DB_host'),
#                  port=env.read_json_data('DB_port'),
#                  database_name=env.read_json_data('DB_database'),
#                  user=env.read_json_data('DB_user'),
#                  password=env.read_json_data('DB_password'))
l_con = LiteConnection(path=os.getenv('path_sqlite_db'))


async def menu_characters(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                  buttons=[['Создать новый лист', 'Список существующих'],
                                           ['Выбрать персонажа для игры'],
                                           ['На главную']],
                                  call_back=[['new_character', 'list_characters'],
                                             ['choice_characters'],
                                             ['start']])
                              )
    await call.message.delete()


async def list_characters(call: types.CallbackQuery):
    # ids = con.work_with_MySQL([f'SELECT id FROM characters_list WHERE user_id='
    #                           f'(SELECT id FROM users WHERE user_id="{call.from_user.id}")'])[0]
    ids = l_con.work_with_SQLite([f'SELECT id FROM characters_list WHERE user_id='
                                  f'(SELECT id FROM users WHERE user_id="{call.from_user.id}")'])[0]
    if len(ids) == 0:
        await call.message.answer(f'У вас ещё нет созданных персонажей!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=[['Создать персонажа', 'Назад'],
                                               ['На главную']], call_back=[['new_character', 'Character'],
                                                                           ['start']])
                                  )
    else:
        # names = con.work_with_MySQL([f'SELECT name_character FROM characters_list '
        #                              f'WHERE user_id = '
        #                              f'(SELECT id FROM users WHERE user_id = "{call.from_user.id}")'])
        # links = con.work_with_MySQL([f'SELECT link FROM characters_list '
        #                              f'WHERE user_id = '
        #                              f'(SELECT id FROM users WHERE user_id = "{call.from_user.id}")'])
        names = l_con.work_with_SQLite([f'SELECT name_character FROM characters_list '
                                        f'WHERE user_id = '
                                        f'(SELECT id FROM users WHERE user_id = "{call.from_user.id}")'])
        links = l_con.work_with_SQLite([f'SELECT link FROM characters_list '
                                        f'WHERE user_id = '
                                        f'(SELECT id FROM users WHERE user_id = "{call.from_user.id}")'])
        await call.message.answer(f'Пожалуйста выберите интерисующий вас лист персонажа:',
                                  reply_markup=BotTools.construction_inline_keyboard_with_link(
                                      list_name=names,
                                      list_link=links))


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


async def new_sheet_character(call: types.CallbackQuery, state: FSMContext):
    if check_verify(call.from_user.id):
        await input_name_character(call=call, state=state)
    else:
        await call.message.answer('Пожалуйста, пройдите верификацию!',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=[['К верификации'],
                                                                                              ['На главную']],
                                                                                     call_back=[['verify'],
                                                                                                ['start']])
                                  )
    await call.answer()
    await call.message.delete()


async def input_name_character(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(states_create_character.StepsCreateCharacter.name)
    await call.message.answer('Введите имя персонажа',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                 call_back=['start']))
    await call.message.delete()


async def create_sheet_character(message: types.Message, state: FSMContext):
    temp = await message.answer(f'Ожидайте...\n'
                                f'Вы можете выйти из меню, но создание персонажа прервётся',
                                reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                                   call_back=['start']))

    await temp.delete()
    await state.update_data(name=message.text)
    data = await state.get_data()
    name_character = data['name']
    sheet = GoogleTools.create_item(item_name=name_character,
                                    mail=f'{check_verify(message.from_user.id)}')
    web_link = sheet['webViewLink']
    sheet_id = sheet['id']
    # con.work_with_MySQL([f'INSERT INTO characters_list(user_id, name_character, link, file_id)'
    #                      f' VALUES((SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
    #                      f' "{name_character}", "{web_link}", "{sheet_id}")'])
    l_con.work_with_SQLite([f'INSERT INTO characters_list(user_id, name_character, link, file_id)'
                            f' VALUES((SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
                            f' "{name_character}", "{web_link}", "{sheet_id}")'])
    await message.answer(f'Ваш документ создан!\n'
                         f'Ссылка на лист персонажа: {web_link}',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                            call_back=['start']))
    await state.clear()
