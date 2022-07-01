from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

tracker_about_button = InlineKeyboardButton(text='Описание', callback_data='get_tracker_about')
track_price_button = InlineKeyboardButton(text='Отлеживать цену товара', callback_data='get_track_price')
untrack_price_button = InlineKeyboardButton(text='Отменить отслеживание', callback_data='untrack_product_price')

stop_tracking_button = InlineKeyboardButton(text='Прекратить отслеживание', callback_data='stop_tracking')
cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')

to_main_menu_button = InlineKeyboardButton(text='<- В главное меню', callback_data='to_main_menu')
to_tracker_menu_button = InlineKeyboardButton(text='<- В меню трекера', callback_data='to_tracker_menu')


tracker_menu = InlineKeyboardMarkup(row_width=1).add(tracker_about_button, track_price_button, untrack_price_button)
stop_tracking_menu = InlineKeyboardMarkup(row_width=1).add(stop_tracking_button)
cancel_menu = InlineKeyboardMarkup(row_width=1).add(cancel_button)
back_to_menu = InlineKeyboardMarkup(row_width=2).add(to_main_menu_button, to_tracker_menu_button)
