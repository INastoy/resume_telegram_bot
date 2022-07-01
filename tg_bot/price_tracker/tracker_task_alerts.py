from asyncio import sleep

from db import Products
from tg_bot.bot import bot


async def send_price_alert(price_alert: dict, tg_user_id: int, product_url) -> None:
    await bot.send_message(
        chat_id=tg_user_id,
        text=f'текущая цена на {price_alert["product_name"]} равна {price_alert["product_new_price"]}'
    )
    await Products.objects.delete(product_url=product_url)
