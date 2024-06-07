from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from Tools.BotTools import Tools

from SQL.Tables import MySQLSession, PlayersStories, GameStories
from sqlalchemy import and_

from States import states_connect_to

from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

BotTools = Tools()


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
    user_id = message.from_user.id

    with MySQLSession.begin() as session:
        if session.query(GameStories.id).filter(and_(GameStories.id == group,
                                                     GameStories.password == password)).first():

            check_GM = session.query(GameStories.gm_id).filter(and_(GameStories.id == group,
                                                                    GameStories.password == password)).first()
            check_user = session.query(PlayersStories.player_id).filter(and_(PlayersStories.player_id == user_id,
                                                                             PlayersStories.story_id == group)).all()
            print(f'check_GM: {check_GM}\n'
                  f'check_user: {check_user}\n'
                  f'{not check_user}')
            if check_GM[0] != user_id and (not check_user or check_user[0] != user_id):
                # expire_date = datetime.now() + timedelta(days=1)
                await message.answer('Создание ссылки...')
                link = await bot.create_chat_invite_link(chat_id=group, member_limit=1)

                await message.answer(f'Приятной игры!\n'
                                     f'Ваша ссылка для подключения к группе - {link.invite_link}',
                                     reply_markup=BotTools.construction_inline_keyboard(buttons=['На главную'],
                                                                                        call_back=['start'])
                                     )
                session.add(PlayersStories(**{"player_id": user_id,
                                              "story_id": group}))
            elif check_GM[0] == user_id or check_user[0] == user_id:
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
