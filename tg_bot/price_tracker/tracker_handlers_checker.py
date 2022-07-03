from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from db import Products, Users
from tg_bot.price_tracker.tracker import get_product_data
from tg_bot.price_tracker.tracker_handlers import Form, process_track_url
from tg_bot.price_tracker.tracker_kb import cancel_menu, stop_tracking_menu
from tg_bot.price_tracker.validators import is_valid_url, validate_url


async def process_track_is_valid_url(message: types.Message) -> types.Message:
    """
    Проверяет введенный пользователем URL на сооветствие минимальным требованиям
    Кнопка: выводится если пользователь ввел невалидный URL или URL другого магазина
    """

    return await message.reply('Повторите попытку!\nПоддерживаются только ссылки на Ситилинк', reply_markup=cancel_menu)


async def process_is_url_exists_or_tracking_already(message: types.Message, state: FSMContext):
    """
    Многокомпонентная функция
    1. Приводит введенный пользователем URL к стандартному формату (https://www.citilink.ru/product/ ...)
    2. Проверяет не отслеживается ли уже данный товар пользователем
    3. Проверяет доступность введенного пользователем URL
    Кнопка: срабатывет при попытке начать отслеживание товара пользователем.
    """

    valid_url: str = validate_url(message.text)
    message.text = validate_url(message.text)

    is_tracking_already = await Products.objects \
        .filter(tg_user_id=message.from_user.id) \
        .filter(product_url=valid_url) \
        .exists()

    if is_tracking_already:
        return await message.reply('Вы уже отслеживаете этот товар. Введите другой адрес'
                                   ' или нажмите кнопку "Прекратить отслеживание"',
                                   reply_markup=stop_tracking_menu)

    user = await Users.objects.filter(tg_user_id=message.from_user.id).select_related('city').first()
    city_code = user.city.city_code
    print(city_code)

    try:
        warning = await message.answer('Ожидайте, идет поиск...')
        product_data: dict = get_product_data(valid_url+city_code)
        await warning.delete()
    except AttributeError:
        return await message.reply('Запрашиваемая страница недоступна.\n'
                                   'Проверьте правильность ввода или повторите попытку позднее',
                                   reply_markup=cancel_menu)

    current_price = product_data["product_new_price"]
    await message.answer(
            f'Название: {product_data["product_name"]}\n'
            f'Старая цена: {product_data["product_old_price"]}:\n'
            f'Текущая цена: {current_price}:\n'
            f'Бонусы:{product_data["product_bonuses"]}'
        )

    async with state.proxy() as data:
        data['product_name'] = product_data["product_name"]
    await process_track_url(message, state, current_price=current_price)


async def process_track_is_valid_price(message: types.Message):
    """
    Проверяет введенную пользователем цену на сооветствие минимальным требованиям
    Кнопка: выводится если пользователь ввел что-то кроме цифр в цену товара
    """

    return await message.reply('Повторите попытку. \nЦена должна содержать только цифры\nНапример: 12000',
                               reply_markup=cancel_menu)


def register_handlers_tracker_check(dp: Dispatcher):
    dp.register_message_handler(process_track_is_valid_url, lambda message: not is_valid_url(message.text),
                                state=Form.product_url)
    dp.register_message_handler(process_is_url_exists_or_tracking_already, state=Form.product_url)
    dp.register_message_handler(process_track_is_valid_price, lambda message: not message.text.isdigit(),
                                state=Form.desired_price)

