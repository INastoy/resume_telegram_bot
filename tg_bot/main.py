import logging

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from tg_bot.bot import bot
from tg_bot.main_menu.menu_handlers import register_handlers_menu
from tg_bot.price_tracker.tracker_handlers import register_handlers_tracker
from tg_bot.price_tracker.tracker_task_alerts import register_handlers_tracker_alert

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


register_handlers_menu(dp)
register_handlers_tracker(dp)
register_handlers_tracker_alert(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
