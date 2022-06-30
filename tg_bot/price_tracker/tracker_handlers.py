from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from celery.result import AsyncResult

from db import Products
from tasks import task_get_product_data
from tg_bot.price_tracker.tracker import get_product_data
from tg_bot.price_tracker.tracker_kb import cancel_menu


class Form(StatesGroup):
    product_code = State()
    desired_price = State()


async def get_about(callback: types.CallbackQuery):
    await callback.message.answer('Здесь должно быть описание функционала трекера')


async def track_price(callback: types.CallbackQuery):
    await Form.product_code.set()
    await callback.message.answer('Введите код товара: \nНапример: 1428565')


async def process_track_is_digit(message: types.Message):
    return await message.reply('Введите код товара(только цифры): \nНапример: 1428565')


async def process_is_tracking_already(message: types.Message, state: FSMContext):
    is_tracking_already = await Products.objects \
        .filter(tg_user_id=message.from_user.id) \
        .filter(product_code=message.text) \
        .exists()

    if is_tracking_already:
        return await message.reply('Вы уже отслеживаете этот товар. Введите другой или нажмите кнопку "Отмена"',
                                   reply_markup=cancel_menu)
    else:
        await process_track_code(message, state)


async def process_track_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['product_code'] = message.text

    await Form.next()
    await message.reply('Введите желаемую цену в рублях: \n Например: 12000')


async def process_track_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desired_price'] = message.text

    warning = await message.answer('Ожидайте, идет поиск...')
    res: dict = get_product_data(data['product_code'])
    await warning.delete()
    await message.answer(
        f'Название: {res["product_name"]}\n'
        f'Старая цена: {res["product_old_price"]}:\n'
        f'Текущая цена: {res["product_new_price"]}:\n'
        f'Бонусы:{res["product_bonuses"]}'
    )
    tg_user_id = message.from_user.id
    product_code = data['product_code']
    desired_price = data['desired_price']
    await state.finish()

    task: AsyncResult = task_get_product_data.apply_async((product_code, desired_price, tg_user_id),
                                                          queue='main',
                                                          countdown=10,
                                                          )

    await message.answer(f'task created {task}')

    await Products.objects.get_or_create(product_code=product_code, task_id=task.task_id, tg_user_id=tg_user_id)

    # task_get_product_data.apply_async(('130', '2000', '749111078'), queue='main',
    #                                   eta=datetime.strptime('22/06/28 23:37:00', '%y/%m/%d %H:%M:%S'))


async def cancel_process_tracking(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await callback.message.answer('Отменено')


def register_handlers_tracker(dp: Dispatcher):
    dp.register_callback_query_handler(get_about, text='get_tracker_about')
    dp.register_callback_query_handler(track_price, text='get_track_price')
    dp.register_message_handler(process_track_is_digit, lambda message: not message.text.isdigit(),
                                state=Form.product_code)
    # dp.register_message_handler(track_already_exists, lambda message: len(message.text) != 7, state=Form.product_code)
    dp.register_message_handler(process_is_tracking_already, state=Form.product_code)
    dp.register_message_handler(process_track_code, state=Form.product_code)
    dp.register_message_handler(process_track_price, state=Form.desired_price)
    dp.async_task(process_track_price)
    dp.register_callback_query_handler(cancel_process_tracking, text='cancel', state='*')
