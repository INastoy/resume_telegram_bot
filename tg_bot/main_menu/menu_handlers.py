from aiogram import types, Dispatcher

from db import Users
from city_parse.db_add_cities import db_filler
from tg_bot.price_tracker.tracker_kb import tracker_menu
from tg_bot.main_menu.menu_kb import main_menu


async def cmd_start(message: types.Message):
    """
    Начало работы с ботом. Выводит главное меню
    """

    await message.answer('Главное меню:', reply_markup=main_menu)
    await db_filler()  #TODO Временное решение для тестового заполнения базы данных кодами городов. Исправить
    if not await Users.objects.get_or_none(tg_user_id=message.from_user.id):
        await Users.objects.create(tg_user_id=message.from_user.id, city=240)


async def get_resume(callback: types.CallbackQuery):

    await callback.message.answer('Ссылка на скачивание резюме:')


async def get_tracker(callback: types.CallbackQuery):
    await callback.message.answer('Меню трекера цен Ситилинк:', reply_markup=tracker_menu)


def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_callback_query_handler(get_resume, text='get_resume')
    dp.register_callback_query_handler(get_tracker, text='get_tracker')
