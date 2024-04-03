from aiogram.fsm.state import StatesGroup, State


class StepsChoice(StatesGroup):
    group = State()
    character = State()