import logging

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from city_parse.db_add_cities import db_filler
from db import metadata, engine
from tg_bot.bot import bot
from tg_bot.main_menu.menu_handlers import register_handlers_menu
from tg_bot.price_tracker.tracker_handlers import register_handlers_tracker
from tg_bot.price_tracker.tracker_handlers_validation import register_handlers_tracker_check

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
metadata.create_all(engine)


register_handlers_menu(dp)
register_handlers_tracker_check(dp)
register_handlers_tracker(dp)


async def on_startup(dp):
    await db_filler()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
