from aiogram.fsm.state import StatesGroup, State


class StepsDonate(StatesGroup):
    info = State()
    cost = State()