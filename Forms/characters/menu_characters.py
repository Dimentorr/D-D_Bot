from aiogram import types
from aiogram.fsm.context import FSMContext

from States import states_create_character

from Tools.BotTools import Tools
from Tools.GoogleAPITools import GoogleTools
from SQL.Tables import MySQLSession, Characters, Verify

from dotenv import load_dotenv

GoogleTools = GoogleTools()

load_dotenv()

BotTools = Tools()


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
    with MySQLSession.begin() as session:
        if data_characters := session.query(Characters.name, Characters.link).filter_by(user_id=call.from_user.id).all():
            names, links = [], []
            for i in data_characters:
                names.append(i[0])
                links.append(i[1])
            await call.message.answer(f'Пожалуйста выберите интерисующий вас лист персонажа:',
                                      reply_markup=BotTools.construction_inline_keyboard_with_link(
                                          list_name=names,
                                          list_link=links))
        else:
            await call.message.answer(f'У вас ещё нет созданных персонажей!',
                                      reply_markup=BotTools.construction_inline_keyboard(
                                          buttons=[['Создать персонажа', 'Назад'],
                                                   ['На главную']], call_back=[['new_character', 'Character'],
                                                                               ['start']])
                                      )


def check_verify(user_id: str | int):
    with MySQLSession.begin() as session:
        if mail := session.query(Verify.gmail).filter_by(user_id=user_id).first():
            return mail[0]
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
    user_id = message.from_user.id
    data = await state.get_data()
    name_character = data['name']
    sheet = GoogleTools.create_item(item_name=name_character,
                                    mail=f'{check_verify(user_id)}')
    web_link = sheet['webViewLink']
    sheet_id = sheet['id']
    with MySQLSession.begin() as session:
        session.add(Characters(**{"id": sheet_id,
                                  "user_id": user_id,
                                  "name": name_character,
                                  "link": web_link}))
    await message.answer(f'Ваш документ создан!\n'
                         f'Ссылка на лист персонажа: {web_link}',
                         reply_markup=BotTools.construction_inline_keyboard(buttons=['Назад'],
                                                                            call_back=['start']))
    await state.clear()
