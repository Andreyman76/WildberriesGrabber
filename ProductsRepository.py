import sqlite3


class ProductsRepository:
    def __init__(self, file_name: str):
        self.__file_name = file_name

        with sqlite3.connect(self.__file_name) as connection:
            cursor = connection.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, last_price INTEGER);')
            connection.commit()

    def update_product_price(self, product_id: int, product_price: int):
        with sqlite3.connect(self.__file_name) as connection:
            cursor = connection.cursor()
            cursor.execute('REPLACE INTO products(id, last_price) VALUES(?, ?);', (product_id, product_price))
            connection.commit()

    def get_product_price(self, product_id: int) -> int:
        with sqlite3.connect(self.__file_name) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT last_price FROM products WHERE id = (?)', (product_id,))
            price = cursor.fetchone()

        return None if price is None else price[0]
