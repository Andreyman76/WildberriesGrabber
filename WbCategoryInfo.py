class WbCategoryInfo:
    def __init__(self, name: str, shard: str, query: str, pages: int, max_price: int):
        self.name = name
        self.shard = shard
        self.query = query
        self.pages = pages
        self.max_price = max_price
