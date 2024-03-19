import asyncio
import logging
from aiogram import Bot, executor, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData

from Schemes.Player import PlayerSheet
from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from States import states_create_character


GoogleTools = GoogleTools()
BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))


async def menu_characters(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Создать новый лист', 'Список существующих'],
                                          ['На главную']],
                                 call_back=[['new_character', 'list_characters'],
                                            ['start']],
                                 message=call.message)
                              )
    await call.answer()
    await call.message.delete()


async def list_characters(call: types.CallbackQuery):
    # test
    ids = con.work_with_MySQL(f'SELECT id FROM character_list WHERE user_id='
                              f'(SELECT id FROM users WHERE user_id="{call.from_user.id}")')[0]
    if len(ids) <= 0:
        await call.message.answer(f'У вас ещё нет созданных персонажей!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=[['Создать персонажа', 'Назад'],
                                               ['На главную']],
                                      call_back=[['new_character', 'Character'],
                                                 ['start']],
                                      message=call.message)
                                  )
    elif len(ids) > 6:
        pass
    else:
        buttons, tags = list(), list()
        for i in range(ids):
            # buttons.append([con.work_with_MySQL(f'SELECT')])
            pass

    await call.message.answer(f'')


async def check_verify(user_id: str):
    mail = con.work_with_MySQL(f'Select gmail FROM verify '
                               f'WHERE user_id = '
                               f'(Select id FROM users '
                               f'WHERE user_id = {user_id})')
    if mail:
        print(mail)
        return mail
    else:
        return None


async def new_sheet_character(call: types.CallbackQuery):
    if await check_verify(call.from_user.id):
        await input_name_character(call=call)
    else:
        await call.message.answer('Пожалуйста, пройдите верификацию!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=[['К верификации'],
                                               ['На главную']],
                                      call_back=[['verify'],
                                                 ['start']],
                                      message=call.message)
                                  )
    await call.answer()
    await call.message.delete()


async def input_name_character(call: types.CallbackQuery):
    await states_create_character.StepsCreateCharacter.name.set()
    await call.message.answer('Введите имя персонажа',
                              reply_markup=BotTools.construction_inline_keyboard(
                                  buttons=['Назад'],
                                  call_back=['Back'],
                                  message=call.message))


async def create_sheet_character(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        name_character = data['name']
    sheet = GoogleTools.create_item(item_name=name_character,
                            mail=f'{check_verify(message.from_user.id)}',
                            role='editor')
    web_link = sheet['webViewLink']
    sheet_id = sheet['id']
    con.work_with_MySQL(f'INSERT INTO characters_list(user_id, name_character, webViewLink, file_id)'
                        f' VALUES("{message.from_user.id}", "{name_character}", "{web_link}", "{sheet_id}")')
    await message.answer(f'Ваш документ создан!\n'
                         f'Ссылка на лист персонажа: {web_link}',
                         reply_markup=BotTools.construction_inline_keyboard(
                             buttons=['Назад'],
                             call_back=['Back'],
                             message=message))
    await state.finish()
