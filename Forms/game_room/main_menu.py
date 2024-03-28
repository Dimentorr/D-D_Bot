from aiogram import types

from Tools.BotTools import Tools

BotTools = Tools()


async def first_menu_game_function(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                  buttons=[['Создать новую', 'Присоединиться'],
                                           ['На главную']], call_back=[['create_new_game', 'connect_to'],
                                                                       ['start']])
                              )
    await call.answer()
    await call.message.delete()
