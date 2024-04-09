from aiogram import types
from aiogram.fsm.context import FSMContext

from Tools.MySqlTools import Connection
from Tools.BotTools import Tools
from Tools.SQLiteTools import Connection as LiteConnection

from States import states_create_group

import pyro

import os
from dotenv import load_dotenv

load_dotenv()

BotTools = Tools()
# con = Connection(host=env.read_json_data('DB_host'),
#                  port=env.read_json_data('DB_port'),
#                  database_name=env.read_json_data('DB_database'),
#                  user=env.read_json_data('DB_user'),
#                  password=env.read_json_data('DB_password'))
l_con = LiteConnection(path=os.getenv('path_sqlite_db'))


def get_username(call: types.CallbackQuery):
    return call.from_user.username


async def create_group_name(call: types.CallbackQuery, state: FSMContext):
    if get_username(call):
        await state.set_state(states_create_group.StepsCreate.name_group)
        await call.message.answer(f'Введите название компании',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                     call_back=['start'])
                                  )
        await call.answer()
        await call.message.delete()
    else:
        await call.message.answer(f'Перед этим вам необходимо задать в настройках ваше имя пользователя\n\n'
                                  f'Для этого вам необходимо пройти следующий путь:\n'
                                  f'Настройки->Аккаунт->Имя пользователя',
                                  reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                     call_back=['start']))
    await call.answer()
    await call.message.delete()


async def create_group_password(message: types.Message, state: FSMContext):
    await state.update_data(name_group=message.text)
    await state.set_state(states_create_group.StepsCreate.password)
    await message.answer(f'Введите пароль от комнаты\n',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'], call_back=['start'])
                         )


async def create_group_repeat_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(states_create_group.StepsCreate.repeat_password)
    await message.answer(f'Повторите пароль от комнаты\n',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'], call_back=['start'])
                         )


async def create_group_check(message: types.Message, state: FSMContext):
    from main import bot
    await state.update_data(repeat_password=message.text)
    data = await state.get_data()
    name = data['name_group']
    password = data['password']
    if password == data['repeat_password']:
        bot_name = os.getenv('BOT_NAME')
        username = message.from_user.username
        await message.answer('Подождите, группа создаётся...')
        try:
            admin_is_gm = (f'@{username}' == os.getenv("ADMIN_USERNAME"))
            id_group = await pyro.supergroup_create(title=name, bot_name=bot_name,
                                                    user_name=f'@{username}', admin_gm=admin_is_gm)
            # con.work_with_MySQL([f'INSERT INTO game_stories (GM_id, name_story, id_group, password) '
            #                      f'VALUES ('
            #                      f'(SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
            #                      f'"{name}",'
            #                      f'"{id_group}",'
            #                      f'"{password}")'])
            l_con.work_with_SQLite([f'INSERT INTO game_stories (GM_id, name_story, id_group, password) '
                                    f'VALUES ('
                                    f'(SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
                                    f'"{name}",'
                                    f'"{id_group}",'
                                    f'"{password}")'])
            await message.answer('Готово!',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                    call_back=['start']))
            await bot.send_message(id_group, f'ID компании: {id_group}\n'
                                             f'Пароль: {password}\n'
                                             f'Для вызова меню напишите команду: !menu')
        except Exception as err:
            await message.answer(f'Произошла ошибка!\n'
                                 f'Ошибка - {err}\n\n'
                                 f'Пожалуйста сообщете об этом администратору',
                                 reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                    call_back=['start']))
    else:
        await message.answer('Пароли не совпадают!',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=[['Попробовать сново'],
                                                                                         ['На главную']],
                                                                                call_back=[['create_new_game'],
                                                                                           ['start']]))
    await state.clear()
