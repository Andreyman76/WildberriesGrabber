import requests
from bs4 import BeautifulSoup
import base64

stores = {}


def main():
    #global stores
    #stores = get_stores_data()
    #get_data('electronic36', 'cat=58513', 1, 100000)

    print(get_free_proxies(1))

    pass


def get_free_proxies(page: int = 1) -> list[str]:
    result = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'http://free-proxy.cz/en/proxylist',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    response = requests.get(f'http://free-proxy.cz/en/proxylist/main/{page}', headers=headers, proxies={'https': '89.43.31.134'}, verify=False)

    if response.status_code != 200:
        raise Exception('Не удалось получить список прокси')

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', id='proxy_list').find('tbody').find_all('tr')

    for row in table:
        try:
            ip = row.find('td').find('script').text
        except Exception as ex:
            print(f'Ошибка во время получения прокси: {ex}')
            continue

        if ip:
            ip = base64.b64decode(ip.split('"')[1]).decode('utf-8')
            port = row.find('span', class_='fport').text
            proxy = f'{ip}:{port}'
            print(proxy)
            result.append(proxy)

    return result


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

