from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsLogin(StatesGroup):
    NAME = State()
    PASSWORD = State()


class StepsReg(StatesGroup):
    NAME = State()
    PASSWORD = State()
    REPEAT_PASSWORD = State()
