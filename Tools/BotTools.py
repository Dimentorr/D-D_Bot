import asyncio
import logging
from aiogram import Bot, Dispatcher, types


class Tools:
    def __init__(self):
        pass

    def construction_keyboard(self, buttons, call_back):
        kb = [[], [], [], [], [], [], []]
        for i in range(len(buttons)):
            if type(buttons[i]) == list:
                for j in range(len(buttons[i])):
                    try:
                        kb[i].append(types.KeyboardButton(text=buttons[i][j],
                                                          callback_data=call_back[i][j]))
                    except Exception as err:
                        print(err)
                        kb[i].append(types.KeyboardButton(text=buttons[i][j],
                                                          callback_data='default'))
            else:
                try:
                    kb[0].append(types.KeyboardButton(text=buttons[i],
                                                      callback_data=call_back[i]))
                except Exception as err:
                    print(err)
                    kb[0].append(types.KeyboardButton(text=buttons[i],
                                                      callback_data='default'))
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True
        )
        return keyboard

    def construction_inline_keyboard(self, buttons, call_back):
        kb = [[], [], [], [], [], [], []]
        for i in range(len(buttons)):
            if type(buttons[i]) == list:
                for j in range(len(buttons[i])):
                    try:
                        kb[i].append(types.InlineKeyboardButton(text=buttons[i][j],
                                                          callback_data=call_back[i][j]))
                    except Exception as err:
                        print(err)
                        kb[i].append(types.InlineKeyboardButton(text=buttons[i][j],
                                                          callback_data='default'))
            else:
                try:
                    kb[0].append(types.InlineKeyboardButton(text=buttons[i],
                                                      callback_data=call_back[i]))
                except Exception as err:
                    print(err)
                    kb[0].append(types.InlineKeyboardButton(text=buttons[i],
                                                      callback_data='default'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard