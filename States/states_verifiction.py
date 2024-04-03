from aiogram.fsm.state import StatesGroup, State


class StepsVerification(StatesGroup):
    gmail = State()
    code = State()
    generate_code = State()
