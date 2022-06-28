from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from celery.result import AsyncResult

from tasks import task_get_product_data
from tg_bot.price_tracker.tracker import get_product_data


class Form(StatesGroup):
    product_code = State()
    desired_price = State()


async def get_about(callback: types.CallbackQuery):
    await callback.message.answer('Здесь должно быть описание функционала трекера')


async def track_price(callback: types.CallbackQuery):
    await Form.product_code.set()
    await callback.message.answer('Введите код товара: \nНапример: 1428565')


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
                                                          countdown=10
                                                          )

    await message.answer(f'task created {task}')


def register_handlers_tracker(dp: Dispatcher):
    dp.register_callback_query_handler(get_about, text='get_tracker_about')
    dp.register_callback_query_handler(track_price, text='get_track_price')
    dp.register_message_handler(process_track_code, state=Form.product_code)
    dp.register_message_handler(process_track_price, state=Form.desired_price)
    dp.async_task(process_track_price)
