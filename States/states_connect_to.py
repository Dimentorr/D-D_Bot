from aiogram.fsm.state import StatesGroup, State


class StepsConnectTo(StatesGroup):
    id = State()
    password = State()