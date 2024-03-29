from db import Products
from tg_bot.bot import bot
from tg_bot.price_tracker.tracker import ProductInfo


async def send_price_alert(price_alert: ProductInfo, tg_user_id: int, product_url: str):
    """
    Отправляет пользователю оповещение о снижении цены товара до желаемого уровня
    Кнопка: нет. выполняется автоматически при успешном выполнении условий в таске
    """
    await bot.send_message(
        chat_id=tg_user_id,
        text=f'Цена на {price_alert.product_name} снизилась до: {price_alert.product_new_price}'
    )
    await Products.objects.delete(product_url=product_url)
