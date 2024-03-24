import json
from WbCategoryInfo import WbCategoryInfo


class ApplicationConfig:
    def __init__(self,
                 admins=None,
                 bot_token: str = '',
                 min_discount: float = 0.2,
                 requests_interval: float = 60,
                 database_file_path: str = 'test.db',
                 proxies: dict = None,
                 categories: list[WbCategoryInfo] = None
                 ):
        if admins is None:
            admins = ['']

        self.admins = admins
        self.bot_token = bot_token
        self.min_discount = min_discount
        self.requests_interval = requests_interval
        self.database_file_path = database_file_path
        self.proxies = {} if proxies is None else proxies
        self.categories = [] if categories is None else [WbCategoryInfo(**i) for i in categories]

    def save(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file, indent=4, ensure_ascii=False)

    @staticmethod
    def load(file_path: str) -> 'ApplicationConfig':
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return ApplicationConfig(**data)
