import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_data import CallbackData


class Tools:
    def __init__(self):
        pass

    def construction_inline_keyboard(self, buttons: list, call_back: list, message: types.Message):
        kb = [[], [], [], [], [], [], [], [], []]
        for i in range(len(buttons)):
            if type(buttons[i]) == list:
                for j in range(len(buttons[i])):
                    try:
                        # print(buttons[i][j])
                        kb[i].append(types.InlineKeyboardButton(buttons[i][j],
                                                                callback_data=
                                                                f'{call_back[i][j]}'))
                    except Exception as err:
                        print(err)
                        kb[i].append(types.InlineKeyboardButton(buttons[i][j],
                                                                callback_data=f'default'))
            else:
                try:
                    kb[0].append(types.InlineKeyboardButton(buttons[i],
                                                            callback_data=
                                                            f'{call_back[i]}'))
                except Exception as err:
                    print(f'BotTools, err - {err}')
                    print(buttons)
                    print(call_back)
                    print(message.from_user.id)
                    kb[0].append(types.InlineKeyboardButton(buttons[i],
                                                            callback_data=f'default'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard
