import os
from ApplicationConfig import ApplicationConfig
from ProductsRepository import ProductsRepository
from WbApiGrabber import WbApiGrabber


def main():
    config_file_path = "config.json"

    if not os.path.exists(config_file_path):
        config = ApplicationConfig()
        config.save(config_file_path)
    else:
        config = ApplicationConfig.load(config_file_path)

    repository = ProductsRepository(config.database_file_path)
    grabber = WbApiGrabber(repository)

    for i in grabber.get_products_at_discount(config.categories, config.min_discount_fraction):
        print(i)

    pass


if __name__ == '__main__':
    main()
