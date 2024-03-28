from aiogram import types


class Tools:
    def __init__(self):
        pass

    def construction_inline_keyboard_for_choice(self, name_buttons: list, start_cd: str, private=True):
        kb = [[]]
        for i in range(len(name_buttons)):
            kb.append([])
            try:
                kb[i].append(types.InlineKeyboardButton(name_buttons[i].split(':')[0],
                                                        callback_data=f'{start_cd}-{name_buttons[i]}'))
            except Exception as err:
                print(f'BotTools, err - {err}')
                kb[i].append(types.InlineKeyboardButton(name_buttons[i],
                                                        callback_data=f'default'))
        if private:
            kb[-1].append(types.InlineKeyboardButton('Назад',
                                                     callback_data=f'start'))
        else:
            kb[-1].append(types.InlineKeyboardButton('Назад',
                                                     callback_data=f'supergroup-menu'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard

    def construction_inline_keyboard_for_supergroup(self, cd: list, name_buttons: list):
        kb = [[]]
        for i in range(len(name_buttons)):
            if type(name_buttons[i]) == list:
                kb.append([])
                for j in range(len(name_buttons[i])):
                    try:
                        kb[i].append(types.InlineKeyboardButton(name_buttons[i][j],
                                                                callback_data=f'supergroup-{cd[i][j]}'))
                    except Exception as err:
                        print(f'BotTools, err - {err}')
                        kb[i].append(types.InlineKeyboardButton(name_buttons[i][j],
                                                                callback_data=f'default'))
            else:
                try:
                    kb[0].append(types.InlineKeyboardButton(name_buttons[i],
                                                            callback_data=f'supergroup-{cd[i]}'))
                except Exception as err:
                    print(f'BotTools, err - {err}')
                    kb[0].append(types.InlineKeyboardButton(name_buttons[i],
                                                            callback_data=f'default'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard

    def construction_inline_keyboard_with_link(self, list_name: list, list_link: list, private=True):
        kb = [[]]
        for i in range(len(list_name)):
            kb.append([])
            try:
                if private:
                    kb[i].append(types.InlineKeyboardButton(list_name[i][0],
                                                            url=f'{list_link[i][0]}'))
                else:
                    kb[i].append(types.InlineKeyboardButton(list_name[i],
                                                            url=f'{list_link[i]}'))

            except Exception as err:
                print(f'BotTools, err - {err}')
                kb[i].append(types.InlineKeyboardButton(list_name[i],
                                                        callback_data=f'default'))
        if private:
            kb[-1].append(types.InlineKeyboardButton('Назад',
                                                     callback_data=f'start'))
        else:
            kb[-1].append(types.InlineKeyboardButton('Назад',
                                                     callback_data=f'supergroup-menu'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard

    def construction_inline_keyboard(self, buttons: list, call_back: list):
        kb = [[]]
        for i in range(len(buttons)):
            if type(buttons[i]) == list:
                kb.append([])
                for j in range(len(buttons[i])):
                    try:
                        kb[i].append(types.InlineKeyboardButton(buttons[i][j],
                                                                callback_data=f'{call_back[i][j]}'))
                    except Exception as err:
                        print(f'BotTools, err - {err}')
                        kb[i].append(types.InlineKeyboardButton(buttons[i][j],
                                                                callback_data=f'default'))
            else:
                try:
                    kb[0].append(types.InlineKeyboardButton(buttons[i],
                                                            callback_data=f'{call_back[i]}'))
                except Exception as err:
                    print(f'BotTools, err - {err}')
                    kb[0].append(types.InlineKeyboardButton(buttons[i],
                                                            callback_data=f'default'))
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
            resize_keyboard=True
        )
        return keyboard
