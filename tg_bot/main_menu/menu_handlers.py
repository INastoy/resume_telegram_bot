from aiogram import types, Dispatcher

from tg_bot.price_tracker.tracker_kb import tracker_menu
from tg_bot.main_menu.menu_kb import main_menu


# @dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Начало работы с ботом. Выводит главное меню
    """

    await message.answer('Главное меню:', reply_markup=main_menu)


# @dp.callback_query_handler(text='get_resume')
async def call_resume(callback: types.CallbackQuery):
    await callback.message.answer('Ссылка на скачивание резюме:')


# @dp.callback_query_handler(text='get_tracker')
async def call_parser(callback: types.CallbackQuery):
    await callback.message.answer('Выберите опцию:', reply_markup=tracker_menu)


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_callback_query_handler(call_resume, text='get_resume')
    dp.register_callback_query_handler(call_parser, text='get_tracker')
