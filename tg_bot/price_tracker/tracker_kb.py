from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

tracker_about_button = InlineKeyboardButton(text='Описание', callback_data='get_tracker_about')
track_price_button = InlineKeyboardButton(text='Отлеживать цену товара', callback_data='get_track_price')
untrack_price_button = InlineKeyboardButton(text='Остановить отслеживание цены', callback_data='cancel_track_price')
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')

tracker_menu = InlineKeyboardMarkup(row_width=1).add(tracker_about_button, track_price_button, untrack_price_button)
cancel_menu = InlineKeyboardMarkup(row_width=1).add(cancel_button)
