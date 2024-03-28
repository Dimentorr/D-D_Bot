from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsChoice(StatesGroup):
    group = State()
    character = State()