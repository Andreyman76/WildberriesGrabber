import requests

stores = {}


def main():
    global stores
    stores = get_stores_data()
    get_data('electronic36', 'cat=58513', 1, 100000)
    pass


def get_data(shard: str, query: str, page: int, max_price: int = None):
    url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1257786&page={page}&sort=popular&spp=30&{query}'

    if max_price is not None:
        url += f'&priceU=0;{max_price}'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wildberries.ru',
        'Referer': 'https://www.wildberries.ru/catalog/elektronika/avtoelektronika',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    response = requests.get(url=url, headers=headers)
    print(get_items(response.json()))
    pass


def get_stores_data() -> dict:
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/stores-data.json'
    headers = {
        'Referer': 'https://www.wildberries.ru/catalog/elektronika/avtoelektronika?sort=popular&page=1&priceU=8300^%^3B1500000',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    response = requests.get(url=url, headers=headers).json()
    result = {i['id'] : i['name'] for i in response}

    return result


def get_items(response: dict) -> list:
    result = [{
        'name': i['name'],
        'rating': i['reviewRating'],
        'feedbacks': i['feedbacks'],
        'url': f'https://www.wildberries.ru/catalog/{i["id"]}/detail.aspx',
        'store': stores[i['wh']],
        'old_price': i['priceU'],
        'new_price': i['salePriceU'],
        'discount': '{discount:.2f}%'.format(discount=((i['priceU'] - i['salePriceU']) * 100.0 / i['priceU']))

    } for i in response['data']['products']]

    return result


if __name__ == '__main__':
    main()

