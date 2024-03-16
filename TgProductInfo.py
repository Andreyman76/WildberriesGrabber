from typing import NamedTuple
from WbPriceRange import WbPriceRange


class TgProductInfo(NamedTuple):
    current_price: int
    old_price: int
    name: str
    discount: float
    store: str
    in_stock: int
    price_history: WbPriceRange
    sizes: int
    rating: float
    reviews: int
    product_url: str
    photo_url: str
