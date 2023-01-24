from bs4 import BeautifulSoup

from db import Cities

all_cities = dict()


async def db_filler():
    if res := await Cities.objects.all():
        for city in res:
            all_cities[city.city_name] = city.id

        return
    with open('city_parse/citilink_cities.html', 'r', encoding='utf8') as file:
        soup = BeautifulSoup(file.read(), 'lxml')
        cities_data = soup.findAll('a', class_='CitiesSearch__item-city')
        city_list = []
        big_cities_id = [240, 330, 271, 114, 152, 256, 397, 283, 329, 321, 385, 197]
        for num, city in enumerate(cities_data):
            is_big_city = False
            city_name = city.find(
                'span', class_='CitiesSearch__typography AdaptiveText Typography Typography_small').text.strip()
            city_code: str = city.get('href').split('/')[-1]
            if num + 1 in big_cities_id:
                is_big_city = True

            print(f'{num + 1}.{city_name} - {city_code}')
            city_list.append(Cities(city_name=city_name, city_code=city_code, is_big_city=is_big_city))

        await Cities.objects.bulk_create(city_list)

        res = await Cities.objects.all()
        for city in res:
            all_cities[city.city_name] = city.id
