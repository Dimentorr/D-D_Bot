from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from Tools.MySqlTools import Connection
from Tools.JsonTools import CatalogJson
from Tools.BotTools import Tools
from Tools.SQLiteTools import Connection as LiteConnection

from States import states_connect_to

BotTools = Tools()
env = CatalogJson(name='file/json/environment.json')
con = Connection(host=env.read_json_data('DB_host'),
                 port=env.read_json_data('DB_port'),
                 database_name=env.read_json_data('DB_database'),
                 user=env.read_json_data('DB_user'),
                 password=env.read_json_data('DB_password'))
l_con = LiteConnection(path='file/db/bot_base.db')


async def linc_group_id(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(states_connect_to.StepsConnectTo.id)
    await call.message.answer(f'Введите id компании\n'
                              f'(попросите вашего Мастера сообщить его вам, если этого не произошло ранее)',
                              reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                 call_back=['start'])
                              )
    await call.answer()
    await call.message.delete()


async def linc_group_password(message: types.Message, state: FSMContext):
    await state.update_data(group_id=message.text)
    await state.set_state(states_connect_to.StepsConnectTo.password)
    await message.answer(f'Введите пароль от комнаты\n'
                         f'(попросите вашего Мастера сообщить его вам, если этого не произошло ранее)',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'], call_back=['start'])
                         )


async def linc_group_check(message: types.Message, state: FSMContext):
    from main import bot
    await state.update_data(password=message.text)
    data = await state.get_data()
    group = data['group_id']
    password = data['password']

    try:
        # check_GM = con.work_with_MySQL([f'SELECT user_id FROM users '
        #                                 f'WHERE id = (SELECT GM_id FROM game_stories '
        #                                 f'WHERE id = (SELECT id FROM game_stories '
        #                                 f'WHERE id_group = "{group}" AND '
        #                                 f'password = "{password}")'
        #                                 f')'])[0][0]
        check_GM = l_con.work_with_SQLite([f'SELECT user_id FROM users '
                                           f'WHERE id = (SELECT GM_id FROM game_stories '
                                           f'WHERE id = (SELECT id FROM game_stories '
                                           f'WHERE id_group = "{group}" AND '
                                           f'password = "{password}")'
                                           f')'])[0][0]
    except IndexError:
        check_GM = -1

    try:
        # check_user = con.work_with_MySQL([f'SELECT user_id FROM users '
        #                                   f'WHERE id = (SELECT player_id FROM players_stories '
        #                                   f'WHERE id = (SELECT id FROM game_stories '
        #                                   f'WHERE id_group = "{group}" AND '
        #                                   f'password = "{password}")'
        #                                   f')'])[0][0]
        check_user = l_con.work_with_SQLite([f'SELECT user_id FROM users '
                                             f'WHERE id = (SELECT player_id FROM players_stories '
                                             f'WHERE id = (SELECT id FROM game_stories '
                                             f'WHERE id_group = "{group}" AND '
                                             f'password = "{password}")'
                                             f')'])[0][0]
    except IndexError:
        check_user = -1

    # is_group = con.work_with_MySQL(
    #     [f'SELECT id FROM game_stories WHERE id_group="{group}" AND password="{password}"'])
    is_group = l_con.work_with_SQLite(
        [f'SELECT id FROM game_stories WHERE id_group="{group}" AND password="{password}"'])

    if (message.from_user.id != int(check_GM)) and (message.from_user.id != int(check_user)) and is_group:
        expire_date = datetime.now() + timedelta(days=1)
        await message.answer('Создание ссылки...')
        link = await bot.create_chat_invite_link(chat_id=group, expire_date=expire_date, member_limit=1)

        await message.answer(f'Приятной игры!\n'
                             f'Ваша ссылка для подключения к группе - {link.invite_link}',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                call_back=['start'])
                             )
        # con.work_with_MySQL([f'INSERT INTO players_stories (player_id, story_id) '
        #                      f'VALUES ('
        #                      f'(SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
        #                      f'(SELECT id FROM game_stories WHERE id_group = "{group}")'
        #                      f')'])
        l_con.work_with_SQLite([f'INSERT INTO players_stories (player_id, story_id) '
                                f'VALUES ('
                                f'(SELECT id FROM users WHERE user_id = "{message.from_user.id}"),'
                                f'(SELECT id FROM game_stories WHERE id_group = "{group}")'
                                f')'])
    elif (message.from_user.id == int(check_GM)) or (message.from_user.id == int(check_user)):
        await message.answer('Вы уже являетесь участником этой компании!',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                call_back=['start']))
    else:
        await message.answer('Неверный id или пароль группы!',
                             reply_markup=BotTools.construction_inline_keyboard(buttons=[['Попробовать сново'],
                                                                                         ['На главную']],
                                                                                call_back=[['connect_to'],
                                                                                           ['start']]))
    await state.clear()
