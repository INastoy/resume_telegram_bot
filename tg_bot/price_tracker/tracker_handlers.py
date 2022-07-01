from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from celery.result import AsyncResult

from db import Products
from tasks import task_get_product_data
from tg_bot.price_tracker.validators import validate_url


class Form(StatesGroup):
    product_url = State()
    desired_price = State()


async def get_about(callback: types.CallbackQuery):
    await callback.message.answer('Здесь должно быть описание функционала трекера')


async def track_price(callback: types.CallbackQuery):
    await Form.product_url.set()
    await callback.message.answer(
        'Отправьте ссылку на интересующий товар: \n'
        'Например: https://www.citilink.ru/product/smartfon-xiaomi-redmi-9c-128gb-4gb-sinii-3g-4g-6-53-and10-802-11-b-g-n-1616355/',
        disable_web_page_preview=True)


async def untrack_product_price(callback: types.CallbackQuery):
    products = await Products.objects.filter(tg_user_id=callback.from_user.id).all()
    if not products:
        return await callback.message.answer('Нет отслеживаемых товаров')
    tracker_menu = InlineKeyboardMarkup(row_width=1)
    for product in products:

        tracker_menu.add(InlineKeyboardButton(text=product.product_name,
                                              callback_data=''.join(['delete_', product.task_id])))
    await callback.message.answer('Отслеживаемые товары:', reply_markup=tracker_menu)


async def delete_tracking_product(callback: types.CallbackQuery):
    if callback.data.startswith('delete_'):
        task_id = callback.data.split('_')[1]
        task = AsyncResult(id=task_id)
        task.revoke()
        await Products.objects.delete(task_id=task_id)
        await callback.message.answer('Товар удален из списка отслеживаемых')


async def process_tracking_cancel(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await callback.message.answer('Отменено')


async def process_track_url(message: types.Message, state: FSMContext, current_price):
    async with state.proxy() as data:
        data['product_url'] = message.text

    await Form.next()
    await message.reply('Введите желаемую цену в рублях: \n Текущая цена: {}'.format(current_price))


async def process_track_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desired_price'] = message.text
    # res: dict = get_product_data(data['product_url'])
    # await message.answer(
    #     f'Название: {res["product_name"]}\n'
    #     f'Старая цена: {res["product_old_price"]}:\n'
    #     f'Текущая цена: {res["product_new_price"]}:\n'
    #     f'Бонусы:{res["product_bonuses"]}'
    # )
    tg_user_id = message.from_user.id
    product_url = data['product_url']
    desired_price = data['desired_price']
    product_name = data['product_name']
    await state.finish()

    task: AsyncResult = task_get_product_data.apply_async((product_url, desired_price, tg_user_id),
                                                          queue='main',
                                                          countdown=10,
                                                          )

    await Products.objects.get_or_create(product_url=product_url,
                                         product_name=product_name,
                                         desired_price=desired_price,
                                         task_id=task.task_id,
                                         tg_user_id=tg_user_id,
                                         )
    await message.answer(f'Товар {product_name} добавлен в список отслеживания\n'
                         f'Как только цена снизится до желаемого уровня, Вы получите сообщение')

    # task_get_product_data.apply_async(('130', '2000', '749111078'), queue='main',
    #                                   eta=datetime.strptime('22/06/28 23:37:00', '%y/%m/%d %H:%M:%S'))


async def stop_process_tracking(callback: types.CallbackQuery, state: FSMContext):
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
    await callback.message.answer('Отслеживание прекращено')


def register_handlers_tracker(dp: Dispatcher):
    dp.register_callback_query_handler(get_about, text='get_tracker_about')
    dp.register_callback_query_handler(track_price, text='get_track_price')
    dp.register_callback_query_handler(untrack_product_price, text='untrack_product_price')
    dp.register_callback_query_handler(delete_tracking_product, lambda callback: True)
    dp.register_message_handler(process_track_url, state=Form.product_url)
    dp.register_message_handler(process_track_price, state=Form.desired_price)
    dp.async_task(process_track_price)
    dp.register_callback_query_handler(stop_process_tracking, text='stop_tracking', state='*')
    dp.register_callback_query_handler(process_tracking_cancel, text='cancel', state='*')
