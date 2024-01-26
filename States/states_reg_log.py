from aiogram.fsm.state import StatesGroup, State


class StepsLogin(StatesGroup):
    NAME = State()
    PASSWORD = State()


class StepsReg(StepsLogin):
    NAME = State()
    PASSWORD = State()
    REPEAT_PASSWORD = State()
