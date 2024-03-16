from typing import NamedTuple


class WbProductInfo(NamedTuple):
    product_id: int
    current_price: int
    old_price: int
    name: str
    store_id: int
    in_stock: int
    rating: float
    reviews: int
    sizes: int
