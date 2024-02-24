from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsCreate(StatesGroup):
    name_group = State()
    password = State()
    repeat_password = State()