import requests
from bs4 import BeautifulSoup
import base64
import json

stores = {}
proxies = {

}


def main():
    global stores
    stores = get_stores_data()
    get_data('electronic36', 'cat=58513', 1, 100000)
    print('COMPLETE')
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

    response = requests.get(f'http://free-proxy.cz/en/proxylist/main/{page}', headers=headers, proxies=proxies,
                            verify=False)

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

        if ip and row.text and 'HTTPS' in row.text:
            ip = base64.b64decode(ip.split('"')[1]).decode('utf-8')
            port = row.find('span', class_='fport').text
            proxy = f'{ip}:{port}'
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

    # response = requests.get(url=url, headers=headers, proxies=proxies)
    # response_json = response.json()

    with open('response.json', 'r', encoding='utf-8') as file:
        response_json = json.load(file)

    items = get_items(response_json)

    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(items, file, ensure_ascii=False, indent=4)

    pass


def get_stores_data() -> dict:
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/stores-data.json'
    headers = {
        'Referer': 'https://www.wildberries.ru/catalog/elektronika/avtoelektronika?sort=popular&page=1&priceU=8300^%^3B1500000',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    # response = requests.get(url=url, headers=headers).json()
    # result = {i['id']: i['name'] for i in response}

    # return result

    with open('stores.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def get_items(response: dict) -> list:
    result = []

    for i in response['data']['products']:
        data = WildberriesApiData(i['id'])
        min_price, max_price = get_prices_from_history(data)
        price = i['salePriceU']
        diff = min_price - price
        discount = diff * 100.0 / min_price if diff > 0 and min_price != 0 else 0.0

        result.append(
        {
            'name': i['name'],
            'rating': i['reviewRating'],
            'feedbacks': i['feedbacks'],
            'url': f'https://www.wildberries.ru/catalog/{i["id"]}/detail.aspx',
            'store': stores[str(i['wh'])],
            'current_price': price,
            'min_price': min_price,
            'max_price': max_price,
            'photo': get_photo_url(data),
            'in_stock': i['volume'],
            'discount': '{discount:.2f}%'.format(discount=discount)
        })
    return result


class WildberriesApiData:
    def __init__(self, id: int):
        self.id = id
        self.vol = id // 100_000
        self.part = id // 1000
        self.basket = self.__get_basket()

    def __get_basket(self) -> str:
        if 0 <= self.vol <= 143:
            return '01'
        elif 144 <= self.vol <= 287:
            return '02'
        elif 288 <= self.vol <= 431:
            return '03'
        elif 432 <= self.vol <= 719:
            return '04'
        elif 720 <= self.vol <= 1007:
            return '05'
        elif 1008 <= self.vol <= 1061:
            return '06'
        elif 1062 <= self.vol <= 1115:
            return '07'
        elif 1116 <= self.vol <= 1169:
            return '08'
        elif 1170 <= self.vol <= 1313:
            return '09'
        elif 1314 <= self.vol <= 1601:
            return '10'
        elif 1602 <= self.vol <= 1655:
            return '11'
        elif 1656 <= self.vol <= 1919:
            return '12'
        else:
            return '13'


def get_photo_url(data: WildberriesApiData) -> str:
    url = f'https://basket-{data.basket}.wbbasket.ru/vol{data.vol}/part{data.part}/{id}/images/big/1.webp'
    return url


def get_prices_from_history(data: WildberriesApiData) -> tuple[int]:
    url = f'https://basket-{data.basket}.wbbasket.ru/vol{data.vol}/part{data.part}/{data.id}/info/price-history.json'

    headers = {
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return 0, 0

    response_json = response.json()
    prices = [i['price']['RUB'] for i in response_json]

    return min(prices), max(prices)


if __name__ == '__main__':
    main()
