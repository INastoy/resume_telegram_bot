import math
from typing import List

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from db import Products, Cities

ITEMS_PER_PAGE = 2

city_cb = CallbackData('city', 'action', 'city_id', 'city_name')
products_cb = CallbackData('product', 'task_id', 'action')
pagination_cb = CallbackData('pagination', 'page', 'action')


tracker_about_button: InlineKeyboardButton = InlineKeyboardButton(text='Описание', callback_data='get_tracker_about')
track_price_button: InlineKeyboardButton = InlineKeyboardButton(text='Отлеживать цену товара',
                                                                callback_data='get_track_price')
traceable_products_button: InlineKeyboardButton = InlineKeyboardButton(text='Отменить отслеживание',
                                                                       callback_data=products_cb.new(
                                                                           task_id='',
                                                                           action='get_traceable_products'))


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
                                                                           track_price_button, traceable_products_button
                                                                           )
stop_tracking_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(stop_tracking_button)
cancel_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1).add(cancel_button)
back_to_menu: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2).add(to_main_menu_button, to_tracker_menu_button)


async def create_big_cities_markup() -> InlineKeyboardMarkup:
    big_cities_menu = InlineKeyboardMarkup(row_width=3)
    big_cities: List[Cities] = await Cities.objects.filter(is_big_city=True).all()
    for city in big_cities:
        big_cities_menu.insert(InlineKeyboardButton
                               (text=city.city_name,
                                callback_data=city_cb.new(action='switch_city', city_id=city.id,
                                                          city_name=city.city_name))
                               )
    big_cities_menu.add(enter_city_name_button)

    return big_cities_menu


async def create_traceable_products_markup(traceable_products) -> InlineKeyboardMarkup:
    traceable_products_menu = InlineKeyboardMarkup(row_width=2)
    for product in traceable_products:
        traceable_products_menu.add(InlineKeyboardButton(
            text=f'{product.product_name}. *Ваша цена*: {product.desired_price}',
            callback_data=products_cb.new(task_id=product.task_id, action='delete_tracking'))
        )
    return traceable_products_menu


async def create_traceable_products_markup_with_pagination(page_num: int, traceable_products: List[Products]):
    next_page_button: InlineKeyboardButton = InlineKeyboardButton(
        text='>', callback_data=pagination_cb.new(page=page_num + 1, action='next_page')
    )
    prev_page_button: InlineKeyboardButton = InlineKeyboardButton(
        text='<', callback_data=pagination_cb.new(page=page_num - 1, action='prev_page')
    )
    from_product = page_num * ITEMS_PER_PAGE - ITEMS_PER_PAGE
    to_product = page_num * ITEMS_PER_PAGE
    products_on_page = traceable_products[from_product:to_product:]
    traceable_products_menu = await create_traceable_products_markup(products_on_page)
    last_page_num = math.ceil(len(traceable_products) / ITEMS_PER_PAGE)
    if page_num == 1:
        traceable_products_menu.row(next_page_button)
    elif page_num == last_page_num:
        traceable_products_menu.row(prev_page_button)
    else:
        traceable_products_menu.row(prev_page_button)
        traceable_products_menu.insert(next_page_button)

    return traceable_products_menu


async def get_traceable_products_menu(callback: types.CallbackQuery, page_num: int = 1):
    traceable_products: List[Products] = await Products.objects.filter(tg_user_id=callback.from_user.id).all()
    if not traceable_products:
        return None

    if len(traceable_products) > ITEMS_PER_PAGE:
        traceable_products_menu = await create_traceable_products_markup_with_pagination(page_num, traceable_products)

    else:
        traceable_products_menu = await create_traceable_products_markup(traceable_products)
    return traceable_products_menu
