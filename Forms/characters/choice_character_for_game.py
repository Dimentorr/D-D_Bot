from aiogram import types
from aiogram.fsm.context import FSMContext

from Tools.BotTools import Tools

from States import states_choice_character

from dotenv import load_dotenv
from SQL.Tables import MySQLSession, PlayersStories, GameStories, Characters, SelectedCharacters
from sqlalchemy import and_

load_dotenv(dotenv_path='.env')

BotTools = Tools()


async def group_choice(call: types.CallbackQuery, state: FSMContext):
    with MySQLSession.begin() as session:
        if story_ids := session.query(PlayersStories.story_id).filter(PlayersStories.player_id == call.from_user.id).all():
            name_buttons = []
            for i in story_ids:
                name_story = session.query(GameStories.name).filter(GameStories.id == i[0]).first()[0]
                name_buttons.append(f'{name_story}:{i[0]}')
            await state.set_state(states_choice_character.StepsChoice.group)
            await call.message.answer(f'Пожалуйста выберите интерисующую вас компанию:',
                                      reply_markup=BotTools.construction_inline_keyboard_for_choice(
                                          name_buttons=name_buttons, start_cd='choice_group'))
        else:
            await call.message.answer(f'Вы пока не являетесь игроком ни в одной известной мне компании!',
                                      reply_markup=BotTools.construction_inline_keyboard(
                                          buttons=['Назад'],
                                          call_back=['start']
                                      ))
    await call.message.delete()


async def character_choice(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(group=call.data)
    data = await state.get_data()
    user_id = call.from_user.id
    with MySQLSession.begin() as session:
        selected_characters_user = []
        for i in session.query(SelectedCharacters.character_id).filter(SelectedCharacters.player_id == user_id).all():
            selected_characters_user.append(i[0])
        if names_and_ids := session.query(Characters.name, Characters.id).filter(and_(
                Characters.user_id == user_id,
                Characters.id.not_in(selected_characters_user)
        )).all():
            name_buttons = [f'{i[0]}:{i[1]}' for i in names_and_ids]
            if check_selected_character := session.query(SelectedCharacters.character_id).filter(and_(
                    SelectedCharacters.story_id == data["group"].split(":")[1],
                    SelectedCharacters.player_id == user_id)).first()[0]:
                name_select_character = session.query(Characters.name).filter(Characters.id == check_selected_character
                                                                              ).first()[0]
                message = (f'!!!ВЫ УЖЕ ВЫБИРАЛИ ДЛЯ ЭТОЙ КОМПАНИИ ПЕРСОНАЖА!!!\n\n'
                           f'КОМПАНИЯ - |{data["group"].split("-")[1].split(":")[0]}|\n'
                           f'ВЫБРАННЫЙ ПЕРСОНАЖ - |{name_select_character}|\n\n'
                           f'ВЫ МОЖЕТЕ ПРОДОЛЖИТЬ ПРИВЯЗКУ ПЕРСОНАЖА, '
                           f'НО В ЭТОМ СЛУЧАИ УЖЕ ВЫБРАННЫЙ ПЕРСОНАЖ БУДЕТ ОТВЯЗАН ОТ ВЫБРАННОЙ КОМПАНИИ\n\n'
                           f'Если вы осознано хотите заменить персонажа для выбранной компании - выберите персонажа:')
            else:
                message = f'Выберите персонажа:'
            await state.set_state(states_choice_character.StepsChoice.character)
            await call.message.answer(message,
                                      reply_markup=BotTools.construction_inline_keyboard_for_choice(
                                          name_buttons=name_buttons, start_cd='choice_character'))
        else:
            await state.clear()
            await call.message.answer(f'У вас пока что нет свободных персонажей!',
                                      reply_markup=BotTools.construction_inline_keyboard(
                                          buttons=[['Создать персонажа'], ['Назад']],
                                          call_back=[['new_character'], ['start']]
                                      ))
    await call.message.delete()


async def save_choice(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(character=call.data)
    data = await state.get_data()
    character_name_id = data["character"].split("-")[1].split(":")
    story_name_id = data["group"].split("-")[1].split(":")
    user_id = call.from_user.id
    with MySQLSession.begin() as session:
        if selected_character := session.query(SelectedCharacters.character_id).filter(and_(
                SelectedCharacters.story_id == data["group"].split(":")[1],
                SelectedCharacters.player_id == user_id)).first()[0]:
            session.query(SelectedCharacters).filter_by(character_id=selected_character).update(
                {"character_id": character_name_id[1]})
        else:
            session.add(SelectedCharacters(**{"story_id": story_name_id[1],
                                              "character_id": character_name_id[1],
                                              "player_id": user_id}))
        await call.message.answer(f'Ваш персонаж - |{character_name_id[0]}|,'
                                  f' теперь привязан к компании - |{story_name_id[0]}|!',
                                  reply_markup=BotTools.construction_inline_keyboard(
                                      buttons=['Назад'],
                                      call_back=['start']
                                  ))
    await call.message.delete()
    await state.clear()
