import re
from collections import namedtuple

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36",
                   "--disable-blink-features": "AutomationControlled"}


def get_club_price(product_soup):
    club_price_info = product_soup.find("div", class_="ProductHeader__link-inner ProductHeader__club-price-title")
    if club_price_info:
        number_list = re.findall("\d", club_price_info.text)
        club_price = ""
        for number in number_list:
            club_price += number
        return int(club_price)


def get_product_name(product_soup):
    product_name = product_soup.find(
            'h1',
            class_='Heading Heading_level_1 ProductHeader__title'
        )
    if product_name:
        return product_name.text.strip()
    product_name = product_soup.find("h1", class_="Heading Heading_level_1 ProductPageTitleSection__text")
    if product_name:
        return product_name.text.strip()


def get_product_info(product_soup):
    price_info = {
        "product_old_price": None,
        "product_new_price": None,
        "product_name": get_product_name(product_soup)
    }

    product_old_price = product_soup.find(
        'span',
        class_="ProductHeader__price-old_current-price js--ProductHeader__price-old_current-price"
    )
    product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price')
    if product_old_price and product_new_price:  # Товар доступен со скидкой
        price_info["product_old_price"] = int(product_old_price.text.strip().replace(' ', ''))

        club_price = get_club_price(product_soup)
        if club_price:
            price_info["product_new_price"] = club_price
        else:
            price_info["product_new_price"] = int(product_new_price.text.strip().replace(' ', ''))
        return price_info

    price = product_soup.find(
        'span',
        class_='ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price'
    )
    if price:  # Цена без скидки
        club_price = get_club_price(product_soup)
        if club_price:
            price_info["product_new_price"] = club_price
            price_info["product_old_price"] = price.text.strip().replace(' ', '')
        else:
            price_info["product_new_price"] = int(price.text.strip().replace(' ', ''))

        return price_info
    else:
        return price_info


def get_product_data(product_url) -> dict:
    response_product = session.get(product_url)
    # print(response_product.status_code)
    # with open("file.html", "wb") as file:
    #     file.write(response_product.content)
    # with open("file.html", "rb") as file:
    #     info = BeautifulSoup(file.read(), 'lxml')
    # product_soup = info
    product_soup = BeautifulSoup(response_product.text, 'lxml')
    product_info = get_product_info(product_soup)
    if product_info.get("product_new_price"):
        product_info["product_bonuses"] = product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    else:
        product_info["product_bonuses"] = None

    ProductInfo = namedtuple("ProductInfo", "product_name product_old_price product_new_price product_bonuses")

    product_info = ProductInfo(**product_info)

    return product_info._asdict()
