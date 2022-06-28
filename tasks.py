import asyncio
from asyncore import loop
from time import sleep

import celery
from aiogram import types
from celery import Celery

from tg_bot.price_tracker.tracker import get_product_data
from tg_bot.price_tracker.tracker_task_alerts import send_price_alert

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.result_backend = 'redis://localhost:6379/0'


@app.task
def add(x, y):
    return x + y


@app.task(bind=True)
def task_get_product_data(self, product_code, desired_price, tg_user_id):
    self.max_retries = None

    async def as_task_get_product_data(product_cod, desired_pric, tg_user_i):
        # sleep(5)
        print('1'*15)
        price_alert = get_product_data(product_code)
        if int(price_alert[2]) <= int(desired_pric):

            print(price_alert)
            await send_price_alert(price_alert, tg_user_id)
        else:
            self.retry(countdown=10)

    asyncio.run(as_task_get_product_data(product_code, desired_price, tg_user_id))
