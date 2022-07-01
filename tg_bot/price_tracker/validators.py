import re


def is_valid_url(message):
    if re.search(r'www\.citilink\.ru/product/.*\d.$', message):
        return True
    else:
        return False


def validate_url(url):
    data = re.findall(r'www\.citilink\.ru/product/.*', url)

    result = ''.join(['https://', data[0]])
    if not result[-1] == '/':
        res = ''.join([result, '/'])
        return res
    return result


# def validate_url1(value: str):
#     pattern = re.compile(r'www\.citilink\.ru/product/.*\d/')
#     print(pattern)
#     values_list = re.search(pattern, value)
#     return values_list
#
# # url = 'www.citilink.ru/product/smartfon-xiaomi-redmi-9a-32gb-zelenyi-1402198'
# # url = 'www_citilink_ru/product/s'
#
# # url = 'https://www.citilink.ru/product/smartfon-xiaomi-redmi-9a-32gb-zelenyi-1402198/'
# # q = is_valid_url(url)
# # print(q)
