from time import sleep

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36"}


def get_product_url(product_code) -> str:
    return URL + product_code


def get_product_data(product_code) -> tuple:
    product_url = get_product_url(product_code)
    # response_product = session.get(product_url)
    # print(response_product.status_code)
    # while response_product.status_code != 200:
    #     sleep(1)
    # product_soup = BeautifulSoup(response_product.text, 'lxml')
    # product_name = product_soup.find('h1', class_='Heading Heading_level_1 ProductHeader__title').text.strip()
    # # product_name = product_soup.find('h1', class_='Heading Heading_level_1').text.strip()
    # product_old_price = product_soup.find('span', class_='ProductHeader__price-old_current-price').text.strip()
    # product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price').text.strip()
    # product_bonuses = product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    product_name = 'name'
    product_old_price = 10000
    product_new_price = 4000
    product_bonuses = 700
    return product_name, product_old_price, product_new_price, product_bonuses

