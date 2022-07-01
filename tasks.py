import asyncio
import logging

from aiogram import types
from celery import Celery, Task
from celery.result import AsyncResult
from celery.schedules import crontab

from tg_bot.price_tracker.tracker import get_product_data
from tg_bot.price_tracker.tracker_task_alerts import send_price_alert

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.control.rate_limit('tasks.task_get_product_data', '3/m')
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.result_backend = 'redis://localhost:6379/0'


@app.task
def add(x, y):
    return x + y


@app.task(bind=True)
def task_get_product_data(self, product_url, desired_price, tg_user_id):
    self.max_retries = None

    async def async_get_product_data():
        try:
            price_alert: dict = get_product_data(product_url)

            if int(price_alert.get('product_new_price')) <= int(desired_price):
                await send_price_alert(price_alert, tg_user_id, product_url)
            else:
                self.retry(countdown=60)
        except AttributeError:
            self.retry(countdown=60)

    asyncio.run(async_get_product_data())


# app.conf.beat_schedule = {
#     'get_track_price': {
#         'task': 'tasks.task_get_product_data',
#         'schedule': crontab(hour='7,16', minute=0),
#         'args': (16, 16),
#     },
# }
