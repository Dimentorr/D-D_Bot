from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsVerification(StatesGroup):
    gmail = State()
    code = State()
    generate_code = State()
