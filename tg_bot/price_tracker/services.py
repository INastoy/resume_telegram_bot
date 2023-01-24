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
