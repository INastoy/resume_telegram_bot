from collections import namedtuple

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36",
                   "--disable-blink-features": "AutomationControlled"}


# @dataclass
# class ProductInfo:
#     product_name: str
#     product_old_price: int
#     product_new_price: int
#     product_bonuses: str


def get_product_info(product_soup):
    price_info = {
        "product_old_price": None,
        "product_new_price": None,
        "product_name": product_soup.find(
            'h1',
            class_='Heading Heading_level_1 ProductHeader__title'
        ).text.strip()
    }

    product_old_price = product_soup.find(
        'span',
        class_="ProductHeader__price-old_current-price js--ProductHeader__price-old_current-price"
    )
    product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price')
    if product_old_price and product_new_price:  # Товар доступен со скидкой
        price_info["product_old_price"] = int(product_old_price.text.strip().replace(' ', ''))
        price_info["product_new_price"] = int(product_new_price.text.strip().replace(' ', ''))
        return price_info

    price = product_soup.find(
        'span',
        class_='ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price'
    )
    if price:  # Цена без скидки
        price_info["product_new_price"] = int(price.text.strip().replace(' ', ''))
        return price_info
    else:
        return price_info


def get_product_data(product_url) -> dict:
    response_product = session.get(product_url)
    product_soup = BeautifulSoup(response_product.text, 'lxml')
    product_info = get_product_info(product_soup)
    if product_info.get("product_new_price"):
        product_info["product_bonuses"] = product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    else:
        product_info["product_bonuses"] = None

    ProductInfo = namedtuple("ProductInfo", "product_name product_old_price product_new_price product_bonuses")

    product_info = ProductInfo(**product_info)

    return product_info._asdict()
