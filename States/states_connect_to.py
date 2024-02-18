from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsConnectTo(StatesGroup):
    id = State()
    password = State()