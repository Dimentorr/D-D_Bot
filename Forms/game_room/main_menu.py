from aiogram import types

from Tools.BotTools import Tools

BotTools = Tools()


async def first_menu_game_function(call: types.CallbackQuery):
    await call.message.answer('Выберите желаемый вариант',
                              reply_markup=BotTools.construction_inline_keyboard(
                                 buttons=[['Мои компании', 'Доступные компании'],
                                          ['Создать новую', 'Присоединиться'],
                                          ['На главную']],
                                 call_back=[['GM_list', 'player_list'],
                                            ['create_new_game', 'connect_to'],
                                            ['start']],
                                 message=call.message)
                              )
    await call.answer()
    await call.message.delete()
