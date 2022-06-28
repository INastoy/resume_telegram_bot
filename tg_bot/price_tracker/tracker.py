from time import sleep

from bs4 import BeautifulSoup
from requests import Session

DOMAIN = 'https://www.citilink.ru/'
URL = 'https://www.citilink.ru/search/?text='

session = Session()
session.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/102.0.0.0 Safari/537.36",
                   "--disable-blink-features": "AutomationControlled"}


def get_product_url(product_code) -> str:
    return URL + product_code


def get_product_data(product_code) -> dict:
    product_url = get_product_url(product_code)
    response_product = session.get(product_url)
    print(response_product.status_code)
    while response_product.status_code != 200:
        sleep(1)
    product_soup = BeautifulSoup(response_product.text, 'lxml')
    product_name = product_soup.find('h1', class_='Heading Heading_level_1 ProductHeader__title').text.strip()
    product_old_price = product_soup.find('span', class_='ProductHeader__price-old_current-price').text.strip()
    product_new_price = product_soup.find('span', class_='ProductHeader__price-default_current-price').text.strip()
    product_bonuses = product_soup.find('div', class_='ProductHeader__bonus-block').text.strip()
    tracker_result = {
        'product_name': product_name,
        'product_old_price': product_old_price,
        'product_new_price': product_new_price,
        'product_bonuses': product_bonuses,
    }

    # with open(r'E:\Learing_python\resume_telegram_bot\products_for_test.txt', 'r', encoding='utf8') as file:
    #     q = file.readline().split(',')
    #     tracker_result = {
    #         'product_name': 'name',
    #         'product_old_price': q[0],
    #         'product_new_price': q[1],
    #         'product_bonuses': q[2],
    #     }
    return tracker_result

