from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified
from celery.result import AsyncResult

from city_parse.db_add_cities import all_cities
from db import Products, Cities, Users
from tasks import task_get_product_data
from tg_bot.main_menu.menu_kb import main_menu
from tg_bot.price_tracker.tracker_kb import back_to_menu, tracker_menu, enter_city_name_button, \
    get_traceable_products_menu, pagination_cb, products_cb, create_big_cities_markup, city_cb
from tg_bot.price_tracker.services import validate_url


class Form(StatesGroup):
    product_url: State = State()
    desired_price: State = State()


class CitySearch(StatesGroup):
    city_name: State = State()


async def get_about(callback: types.CallbackQuery) -> types.Message:
    """
    Выводит подробное описание функционала трекера цен.
    Кнопка: "Описание"
    """

    return await callback.message.answer(
        'Трекер предназначен для отслеживания цен на интересующий Вас товар\n'
        'На данный момент реализовано отслеживание для магазина Ситилинк\n'
        'Для начала работы нажмите "Отслеживать цену товара" и следуйте инструкциям на экране',
        reply_markup=back_to_menu
    )


async def get_cities_list(callback: types.CallbackQuery) -> types.Message:
    """
        Выводит список городов. Позволяет пользователю отлеживать цену товара в своем городе
        Кнопка: "Выбрать город"
    """
    big_cities_menu = await create_big_cities_markup()
    cur_city: Cities = await Cities.objects.select_related('user')\
        .get_or_none(Cities.user.tg_user_id == callback.from_user.id)
    return await callback.message.answer(f'Выберите название вашего города:\nТекущий город: {cur_city.city_name}',
                                         reply_markup=big_cities_menu)


async def switch_city(callback: types.CallbackQuery, callback_data: dict) -> types.Message:
    """
    Меняет город отслеживания на выбранный пользователем
    Кнопка: *Название города*
    """
    city_id = callback_data.get('city_id')
    city_name = callback_data.get('city_name')
    await Users.objects.filter(tg_user_id=callback.from_user.id).update(city=city_id)
    return await callback.message.answer(f'Ваш город успешно изменен на {city_name}', reply_markup=back_to_menu)


async def enter_city_name(callback: types.CallbackQuery) -> types.Message:
    """
    Запрашивает у пользователя название города, если он не сделал выбор из предложенных в списке
    Кнопка: "Поиск по городам"
    """

    await CitySearch.city_name.set()
    return await callback.message.answer('Введите название вашего города')


async def searching_city(message: types.Message, state: FSMContext) -> types.Message:
    """
    Выполняет поиск указанного пользователем города по базе.
    Кнопка: нет. Выполняется при вводе названия города.
    """
    new_city = message.text.capitalize()
    city_id = all_cities.get(new_city)
    await Users.objects.filter(Users.tg_user_id == message.from_user.id).update(city=city_id)
    await state.finish()
    return await message.answer(f'Город успешно изменён на {new_city}', reply_markup=back_to_menu)


async def track_price(callback: types.CallbackQuery) -> types.Message:
    """
    Запускает цепочку взаимодействий с пользователем для начала отслеживания цены на товар.
    Кнопка: "Отслеживать цену товара"
     """

    await Form.product_url.set()
    return await callback.message.answer(
        'Отправьте ссылку на интересующий товар: \n'
        'Например: https://www.citilink.ru/product/'
        'smartfon-xiaomi-redmi-9c-128gb-4gb-sinii-3g-4g-6-53-and10-802-11-b-g-n-1616355/',
        disable_web_page_preview=True)


async def get_traceable_products(callback: types.CallbackQuery, callback_data: dict) -> types.Message:
    """
    Выводит список отслеживаемых пользователем товаров для возможности прекращения отслеживания.
    Кнопка: "Отменить отслеживание"
    """
    page_num = int(callback_data.get('page', 1))
    traceable_products_menu = await get_traceable_products_menu(callback, page_num)
    if not traceable_products_menu:
        return await callback.message.answer('Нет отслеживаемых товаров', reply_markup=back_to_menu)
    elif callback.message.text == 'Отслеживаемые товары:':
        return await callback.message.edit_text('Отслеживаемые товары:', reply_markup=traceable_products_menu)

    return await callback.message.answer('Отслеживаемые товары:', reply_markup=traceable_products_menu)


async def delete_traceable_product(callback: types.CallbackQuery, callback_data: dict) -> types.Message:
    """
    Удаляет товар из списка отслеживаемых
    Кнопка: *Название товара*
    """
    task_id = callback_data.get('task_id', None)
    task: AsyncResult = AsyncResult(id=task_id)
    task.revoke()
    await Products.objects.delete(task_id=task_id)
    await callback.message.edit_text(callback.message.text, reply_markup=await get_traceable_products_menu(callback))
    return await callback.message.answer('Товар удален из списка отслеживаемых', reply_markup=back_to_menu)


async def cancel_process(callback: types.CallbackQuery, state: FSMContext) -> types.Message:
    """
    Позволяет прервать цепочку взаимодействия с пользователем при вводе данных товара для отслеживания.
    Кнопка: выводится во время цепочки взаимодействия с пользователем, если тот ввел неправильный URl или цену товара.
    """
    current_state: state = await state.get_state()
    if current_state is None:
        return await callback.message.answer('Отменено', reply_markup=back_to_menu)

    await state.finish()
    return await callback.message.answer('Отменено', reply_markup=back_to_menu)


async def process_track_url(message: types.Message, state: FSMContext):
    """
    Сохраняет валидированный URL от пользователя в машину состояний.
    Кнопка: выводится автоматически после успешной валидации URL, введенного пользователем
    """

    async with state.proxy() as data:
        data['product_url'] = message.text
        product_data = data['product_data']

    if product_data.is_product_in_stock:
        await message.answer(
            f'Название: {product_data.product_name}\n'
            f'Старая цена: {product_data.product_old_price if product_data.product_old_price else "Неизвестно"}:\n'
            f'Текущая цена: {product_data.product_new_price}:\n'
            f'Бонусы: {product_data.product_bonuses}'
        )
    else:
        await message.answer(
            f'Название: {product_data.product_name}\n'
            f'Текущая цена: Товара нет в наличии.\n'
            f'Статус: {product_data.was_last_in_stock}:\n'
        )
    await Form.next()
    await message.reply('Введите желаемую цену в рублях: \n Текущая цена: {}'.format(
        product_data.product_new_price if product_data.product_new_price else 'Неизвестно'))


async def process_track_price(message: types.Message, state: FSMContext):
    """
    Сохраняет валидированную цену от пользователя в машину состояний.
    Кнопка: выводится автоматически после успешной валидации цены, введенной пользователем
    """

    async with state.proxy() as data:
        data['desired_price'] = message.text
    raise SkipHandler


async def process_start_tracking(message: types.Message, state: FSMContext):
    """
    Создает task для ослеживания цены товара
    Кнопка: выполняется автоматически после сохрарнения цены в машину состояний
    """
    async with state.proxy() as data:
        product_data = data['product_data']

    tg_user_id = message.from_user.id
    product_url = data['product_url']
    desired_price = int(data['desired_price'])
    product_name = product_data.product_name
    await state.finish()

    task: AsyncResult = task_get_product_data.apply_async(
        (product_url, desired_price, tg_user_id), queue='main', countdown=10
    )

    await Products.objects.create(product_url=product_url, product_name=product_name, desired_price=desired_price,
                                  task_id=task.task_id, tg_user_id=tg_user_id)

    await message.answer(f'Товар {product_name} добавлен в список отслеживания\n'
                         f'Как только цена снизится до желаемого уровня, Вы получите сообщение',
                         reply_markup=back_to_menu)


async def stop_process_tracking(callback: types.CallbackQuery, state: FSMContext):
    """
    Останавливает отслеживание товара.
    Кнопка: выводится если пользователь пытается добавить URL на товар, который уже отслеживается.
    """

    current_state = await state.get_state()
    if current_state is None:
        return
    url = validate_url(callback.message.reply_to_message.text)
    tg_user_id = callback.from_user.id

    tracked_product = await Products.objects.filter(product_url=url, tg_user_id=tg_user_id).first()
    task_id = tracked_product.task_id
    task = AsyncResult(id=task_id)
    task.revoke()

    await Products.objects.delete(product_url=url)
    await state.finish()
    await callback.message.answer('Отслеживание прекращено', reply_markup=back_to_menu)


async def to_main_menu(callback: types.CallbackQuery):
    """
    Позволяет пользователю вернуться в главное меню
    Кнопка: "<- В главное меню"
    """
    return await callback.message.answer('Главное меню:', reply_markup=main_menu)


async def to_tracker_menu(callback: types.CallbackQuery):
    """
    Позволяет пользователю вернуться в меню трекера
    Кнопка: "<- В меню трекера"
    """
    return await callback.message.answer('Меню трекера цен Ситилинк:', reply_markup=tracker_menu)


async def message_not_modified_handler(update, error):
    return True


async def invalid_input(message: types.Message):
    """
    Выводит кнопки навигации по боту.
    Кнопка: выводится если пользователь ввел неизвестное сообщение и другие обработчики ошибок не обработали сообщение
    """
    return await message.reply('Неизвестная команда\nДля вызова меню нажмите на /start:')


def register_handlers_tracker(dp: Dispatcher):
    dp.register_callback_query_handler(get_about, text='get_tracker_about')
    dp.register_callback_query_handler(get_cities_list, text='get_cities_list')
    dp.register_callback_query_handler(switch_city, city_cb.filter(action='switch_city'))
    dp.register_callback_query_handler(enter_city_name, text='enter_city_name')
    dp.register_message_handler(searching_city, state=CitySearch.city_name)
    dp.register_callback_query_handler(track_price, text='get_track_price')
    dp.register_callback_query_handler(get_traceable_products, products_cb.filter(action='get_traceable_products'))
    dp.register_callback_query_handler(get_traceable_products, pagination_cb.filter(action=['next_page', 'prev_page']))
    dp.register_callback_query_handler(to_main_menu, text='to_main_menu')
    dp.register_callback_query_handler(to_tracker_menu, text='to_tracker_menu')
    # dp.register_callback_query_handler(delete_traceable_product, text_startswith='delete_')
    dp.register_callback_query_handler(delete_traceable_product, products_cb.filter(action='delete_tracking'))
    dp.register_message_handler(process_track_url, state=Form.product_url)
    dp.register_message_handler(process_track_price, state=Form.desired_price)
    dp.register_message_handler(process_start_tracking, state=Form.desired_price)
    dp.register_callback_query_handler(stop_process_tracking, text='stop_tracking', state='*')
    dp.register_callback_query_handler(cancel_process, text='cancel', state='*')
    dp.register_errors_handler(message_not_modified_handler, exception=MessageNotModified)
    dp.register_message_handler(invalid_input)
