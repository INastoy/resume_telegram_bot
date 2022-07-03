from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

tracker_about_button: InlineKeyboardButton = InlineKeyboardButton(text='Описание', callback_data='get_tracker_about')
track_price_button: InlineKeyboardButton = InlineKeyboardButton(text='Отлеживать цену товара',
                                                                callback_data='get_track_price')
untrack_price_button: InlineKeyboardButton = InlineKeyboardButton(text='Отменить отслеживание',
                                                                  callback_data='untrack_product_price')
cities_list_button: InlineKeyboardButton = InlineKeyboardButton(text='Выбрать город', callback_data='get_cities_list')
enter_city_name_button: InlineKeyboardButton = InlineKeyboardButton(text='Поиск по городам',
                                                                    callback_data='enter_city_name')


stop_tracking_button: InlineKeyboardButton = InlineKeyboardButton(text='Прекратить отслеживание',
                                                                  callback_data='stop_tracking')
cancel_button: InlineKeyboardButton = InlineKeyboardButton(text='Отмена', callback_data='cancel')


to_main_menu_button: InlineKeyboardButton = InlineKeyboardButton(text='<- В главное меню', callback_data='to_main_menu')
to_tracker_menu_button: InlineKeyboardButton = InlineKeyboardButton(text='<- В меню трекера',
                                                                    callback_data='to_tracker_menu')


tracker_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(tracker_about_button, cities_list_button,
                                                                           track_price_button, untrack_price_button)
stop_tracking_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(stop_tracking_button)
cancel_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(cancel_button)
back_to_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2).add(to_main_menu_button, to_tracker_menu_button)
