from aiogram import types, Dispatcher
from aiogram.types import ParseMode

from db import Users, Cities
from tg_bot.price_tracker.tracker_kb import tracker_menu
from tg_bot.main_menu.menu_kb import main_menu


async def cmd_start(message: types.Message):
    """
    Начало работы с ботом. Выводит главное меню
    """

    await message.answer('Главное меню:', reply_markup=main_menu)
    await Users.objects.get_or_create(tg_user_id=message.from_user.id, city=Cities(id=1))


async def get_resume(callback: types.CallbackQuery):

    await callback.message.answer('Ссылка на скачивание резюме:')


async def get_tracker(callback: types.CallbackQuery):
    await callback.message.answer('Меню трекера цен Ситилинк:', reply_markup=tracker_menu)


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_callback_query_handler(get_resume, text='get_resume')
    dp.register_callback_query_handler(get_tracker, text='get_tracker')
