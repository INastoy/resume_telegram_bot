import re
from dataclasses import dataclass
from typing import Type, Union

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36",
                   "--disable-blink-features": "AutomationControlled"}


@dataclass
class ProductInfo:
    product_name: str
    is_product_in_stock: bool
    was_last_in_stock: str
    product_old_price: int = None
    product_new_price: int = None
    product_bonuses: int = None


def get_club_price(product_soup: BeautifulSoup) -> int:
    club_price_info = product_soup.find("div", class_="ProductHeader__link-inner ProductHeader__club-price-title")
    if club_price_info:
        number_list = re.findall("\d", club_price_info.text)
        club_price = ""
        for number in number_list:
            club_price += number
        return int(club_price)


def get_product_name(product_soup: BeautifulSoup) -> str:
    product_name = product_soup.find(
        'h1',
        class_='Heading Heading_level_1 ProductHeader__title'
    )
    if product_name:
        return product_name.text.strip()
    product_name = product_soup.find("h1", class_="Heading Heading_level_1 ProductPageTitleSection__text")
    if product_name:
        return product_name.text.strip()


def is_in_stock(product_soup: BeautifulSoup) -> bool:
    soup = product_soup.find('h2', class_='ProductHeader__not-available-header')
    if soup:
        text = soup.text.strip()
        if text == 'Нет в наличии':
            return False
    return True


def get_last_in_stock(product_soup: BeautifulSoup) -> str:
    last_in_stock = product_soup.find('div', class_='ProductHeader__not-available-date')
    if last_in_stock:
        return last_in_stock.text.strip()
    else:
        return 'Нет данных'


def get_product_price(product_soup: BeautifulSoup):
    product_old_price = product_soup.find(
        'span',
        class_="ProductHeader__price-old_current-price js--ProductHeader__price-old_current-price"
    )
    product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price')
    if product_old_price and product_new_price:  # Товар доступен со скидкой
        ProductInfo.product_old_price = int(product_old_price.text.strip().replace(' ', ''))

        club_price = get_club_price(product_soup)
        if club_price:
            ProductInfo.product_new_price = club_price
        else:
            ProductInfo.product_new_price = int(product_new_price.text.strip().replace(' ', ''))
        return ProductInfo

    price = product_soup.find(
        'span',
        class_='ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price'
    )
    if price:  # Цена без скидки
        club_price = get_club_price(product_soup)
        if club_price:
            ProductInfo.product_new_price = club_price
            ProductInfo.product_old_price = price.text.strip().replace(' ', '')
        else:
            ProductInfo.product_new_price = int(price.text.strip().replace(' ', ''))


def get_product_bonuses(product_soup) -> Union[None, str]:
    if ProductInfo.product_new_price:
        return product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    else:
        return None


def get_product_data(product_url) -> Type[ProductInfo]:
    response_product = session.get(product_url)
    product_soup = BeautifulSoup(response_product.text, 'lxml')

    ProductInfo.product_name = get_product_name(product_soup)
    ProductInfo.is_product_in_stock = is_in_stock(product_soup)
    if not ProductInfo.is_product_in_stock:
        ProductInfo.was_last_in_stock = get_last_in_stock(product_soup)
        return ProductInfo
    get_product_price(product_soup)
    ProductInfo.product_bonuses = get_product_bonuses(product_soup)

    return ProductInfo
