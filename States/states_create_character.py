from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsCreateCharacter(StatesGroup):
    name = State()
