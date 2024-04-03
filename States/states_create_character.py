from aiogram.fsm.state import StatesGroup, State


class StepsCreateCharacter(StatesGroup):
    name = State()
