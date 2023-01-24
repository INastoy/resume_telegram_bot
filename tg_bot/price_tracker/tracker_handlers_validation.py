from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import SkipHandler

from city_parse.db_add_cities import all_cities
from db import Products, Cities
from tg_bot.price_tracker.tracker import get_product_data, ProductInfo
from tg_bot.price_tracker.tracker_handlers import Form, CitySearch
from tg_bot.price_tracker.tracker_kb import cancel_menu, stop_tracking_menu
from tg_bot.price_tracker.services import is_valid_url, validate_url


async def process_is_valid_city(message: types.Message) -> types.Message:
    return await message.reply('Указанный Вами город не найден\n Повторите попытку', reply_markup=cancel_menu)


async def process_track_is_valid_url(message: types.Message) -> types.Message:
    """
    Проверяет введенный пользователем URL на сооветствие минимальным требованиям
    Кнопка: выводится если пользователь ввел невалидный URL или URL другого магазина
    """

    return await message.reply('Повторите попытку!\nПоддерживаются только ссылки на Ситилинк', reply_markup=cancel_menu)


async def process_url_validation(message: types.Message):
    """
    Приводит введенный пользователем URL к стандартному формату (https://www.citilink.ru/product/ ...)
    Кнопка: срабатывает после ввода пользователем URL
    """
    message.text = validate_url(message.text)
    raise SkipHandler


async def process_is_tracking_already(message: types.Message):
    """
    Проверяет не отслеживается ли уже данный товар пользователем
    Кнопка: срабатывает после ввода пользователем URL
    """
    is_tracking_already: Products = await Products.objects \
        .filter(tg_user_id=message.from_user.id) \
        .filter(product_url=message.text) \
        .exists()
    if is_tracking_already:
        return await message.reply('Вы уже отслеживаете этот товар. Введите другой адрес'
                                   ' или нажмите кнопку "Прекратить отслеживание"',
                                   reply_markup=stop_tracking_menu)
    else:
        raise SkipHandler


async def process_is_url_exist(message: types.Message, state: FSMContext):
    """
    Проверяет доступность введенного пользователем URL, сохраняет результат запроса
    Кнопка: срабатывает после ввода пользователем URL
    """
    cur_city: Cities = await Cities.objects.select_related('user')\
        .get_or_none(Cities.user.tg_user_id == message.from_user.id)

    try:
        warning = await message.answer('Ожидайте, идет поиск...')
        product_data: ProductInfo = get_product_data(message.text + cur_city.city_code)
        await warning.delete()
    except AttributeError:
        return await message.reply('Запрашиваемая страница недоступна.\n'
                                   'Проверьте правильность ввода или повторите попытку позднее',
                                   reply_markup=cancel_menu)
    async with state.proxy() as data:
        data['product_data'] = product_data
    raise SkipHandler


async def process_track_is_valid_price(message: types.Message):
    """
    Проверяет введенную пользователем цену на сооветствие минимальным требованиям
    Кнопка: выводится если пользователь ввел что-то кроме цифр в цену товара
    """

    return await message.reply('Повторите попытку. \nЦена должна содержать только цифры\nНапример: 12000',
                               reply_markup=cancel_menu)


def register_handlers_tracker_check(dp: Dispatcher):
    dp.register_message_handler(process_is_valid_city, lambda message: message.text.capitalize() not in all_cities,
                                state=CitySearch)
    dp.register_message_handler(process_track_is_valid_url, lambda message: not is_valid_url(message.text),
                                state=Form.product_url)
    dp.register_message_handler(process_url_validation, state=Form.product_url)
    dp.register_message_handler(process_is_tracking_already, state=Form.product_url)
    dp.register_message_handler(process_is_url_exist, state=Form.product_url)
    dp.register_message_handler(process_track_is_valid_price, lambda message: not message.text.isdigit(),
                                state=Form.desired_price)

