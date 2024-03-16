import requests

from ProductsRepository import ProductsRepository
from TgProductInfo import TgProductInfo
from WbCategoryInfo import WbCategoryInfo
from WbPriceRange import WbPriceRange
from WbProductInfo import WbProductInfo


class WbApiGrabber:
    __stores = {}
    __proxies = {}

    def __init__(self, repository: ProductsRepository, proxies=None):
        self.repository = repository

        if proxies is None:
            proxies = {}

        self.__proxies = proxies

    def get_products_at_discount(self, categories: list[WbCategoryInfo], min_discount: float) -> list[TgProductInfo]:
        for category in categories:
            for product in self.__get_products(category):
                old_price = self.repository.get_product_price(product.product_id)

                if old_price is not None and (old_price - product.current_price) / old_price >= min_discount:
                    product_info = self.__get_product_info(product)

                    if product_info.current_price <= product_info.price_history.min_price:
                        yield product_info

                self.repository.update_product_price(product.product_id, product.current_price)
        pass

    def __get_products(self, category: WbCategoryInfo) -> list[WbProductInfo]:
        url = f'https://catalog.wb.ru/catalog/{category.shard}/v2/catalog'

        query_key, query_value = category.query.split('=')
        params = {
            'appType': '1',
            'curr': 'rub',
            'dest': '-1257786',
            'sort': 'popular',
            'spp': '30',
            query_key: query_value
        }

        if category.max_price is not None:
            params['priceU'] = f'0;{category.max_price}'

        for page in range(category.pages):
            params['page'] = page + 1

            response = requests.get(url, params=params, proxies=self.__proxies)

            if response.status_code != 200:
                continue

            response_json = response.json()
            products = response_json['data']['products']

            print(f'{category.name}, стр {page + 1}: {len(products)} шт')

            for product in products:
                sizes = product.get('sizes')
                price = sizes[0].get('price')

                yield WbProductInfo(
                    product_id=product.get('id'),
                    current_price=price.get('product'),
                    old_price=price.get('basic'),
                    name=product.get('name'),
                    store_id=product.get('wh'),
                    in_stock=product.get('volume'),
                    rating=product.get('reviewRating'),
                    reviews=product.get('feedbacks'),
                    sizes=len(sizes)
                )

    def __get_product_info(self, info: WbProductInfo) -> TgProductInfo:
        vol = info.product_id // 100_000
        part = info.product_id // 1000
        basket = self.__get_basket(vol)

        price_history = self.__get_prices_from_history(info.product_id, vol, part, basket)
        discount_start = info.old_price
        diff = discount_start - info.current_price
        discount = diff * 100.0 / discount_start if diff > 0 and discount_start != 0 else 0.0

        if info.store_id not in self.__stores.keys():
            self.__load_stores_data()

        store = self.__stores.get(info.store_id)

        if store is None:
            store = "NOT FOUND"

        return TgProductInfo(
            current_price=info.current_price,
            old_price=info.old_price,
            name=info.name,
            discount=discount,
            store=store,
            in_stock=info.in_stock,
            price_history=price_history,
            sizes=info.sizes,
            rating=info.rating,
            reviews=info.reviews,
            product_url=f'https://www.wildberries.ru/catalog/{info.product_id}/detail.aspx',
            photo_url=self.__get_photo_url(info.product_id, vol, part, basket)
        )

    def __load_stores_data(self):
        url = 'https://static-basket-01.wbbasket.ru/vol0/data/stores-data.json'
        response = requests.get(url).json()

        if response.status_code == 200:
            self.__stores = {i['id']: i['name'] for i in response}
        pass

    @staticmethod
    def __get_basket(vol: int) -> str:
        if 0 <= vol <= 143:
            return '01'
        elif 144 <= vol <= 287:
            return '02'
        elif 288 <= vol <= 431:
            return '03'
        elif 432 <= vol <= 719:
            return '04'
        elif 720 <= vol <= 1007:
            return '05'
        elif 1008 <= vol <= 1061:
            return '06'
        elif 1062 <= vol <= 1115:
            return '07'
        elif 1116 <= vol <= 1169:
            return '08'
        elif 1170 <= vol <= 1313:
            return '09'
        elif 1314 <= vol <= 1601:
            return '10'
        elif 1602 <= vol <= 1655:
            return '11'
        elif 1656 <= vol <= 1919:
            return '12'
        else:
            return '13'

    @staticmethod
    def __get_photo_url(product_id: int, vol: int, part: int, basket: str) -> str:
        url = f'https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/images/big/1.webp'
        return url

    @staticmethod
    def __get_prices_from_history(product_id: int, vol: int, part: int, basket: str) -> WbPriceRange:
        url = f'https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/info/price-history.json'
        response = requests.get(url)

        if response.status_code != 200:
            return WbPriceRange(
                min_price=0,
                max_price=0
            )

        response_json = response.json()
        prices = [int(i['price']['RUB']) for i in response_json]

        return WbPriceRange(
            min_price=min(prices),
            max_price=max(prices)
        )
