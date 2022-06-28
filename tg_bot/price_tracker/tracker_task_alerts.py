from aiogram import types, Dispatcher

from tg_bot.bot import bot


async def send_price_alert(price_alert, tg_user_id):
    print('send price alert')
    await bot.send_message(chat_id=tg_user_id, text=f'текущая цена на {price_alert[0]} равна {price_alert[2]}')


def register_handlers_tracker_alert(dp: Dispatcher):
    dp.register_message_handler(send_price_alert)


