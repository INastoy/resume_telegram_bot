from time import sleep

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36",
                   "--disable-blink-features": "AutomationControlled"}


def get_price_info(product_soup):
    price_info = {
        "price": None,
        "product_old_price": None,
        "product_new_price": None,
        "available": True
    }

    product_old_price = product_soup.find(
        'span',
        class_='ProductHeader__price-old_current-price js--ProductHeader__price-old_current-price'
    )
    product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price')
    if product_old_price and product_new_price:  # Товар доступен со скидкой
        price_info["product_old_price"] = int(product_old_price.text.strip().replace(' ', ''))
        price_info["product_new_price"] = int(product_new_price.text.strip().replace(' ', ''))
        return price_info

    product_new_price = product_soup.find(
        'span',
        class_='ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price'
    )
    if product_new_price:  # Цена без скидки
        price_info["product_new_price"] = int(product_new_price.text.strip().replace(' ', ''))
        return price_info
    else:
        price_info["available"] = False
        return price_info


def get_product_data(product_url) -> dict:
    response_product = session.get(product_url)
    with open("file.html", "wb") as file:
        file.write(response_product.content)
    # if response_product.status_code == 429:
    #     print(response_product.text)
    # while response_product.status_code != 200:
    #     sleep(1)
    product_soup = BeautifulSoup(response_product.text, 'lxml')
    price_info = get_price_info(product_soup)
    product_name = product_soup.find('h1', class_='Heading Heading_level_1 ProductHeader__title').text.strip()
    if price_info.get("available"):
        product_bonuses = product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    else:
        product_bonuses = None
    tracker_result = {
        'product_name': product_name,
        'product_bonuses': product_bonuses,
    }
    tracker_result.update(price_info)

    return tracker_result
