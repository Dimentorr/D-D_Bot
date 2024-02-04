from aiogram.dispatcher.filters.state import StatesGroup, State


class StepsLogin(StatesGroup):
    name = State()
    password = State()


class StepsReg(StatesGroup):
    name = State()
    password = State()
    repeat_password = State()
