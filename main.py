import os
from ApplicationConfig import ApplicationConfig
from Logger import Logger
from ProductsRepository import ProductsRepository
from TgBot import TgBot
from WbApiGrabber import WbApiGrabber


def main():
    try:
        config_file_path = "config.json"

        if not os.path.exists(config_file_path):
            config = ApplicationConfig()
            config.save(config_file_path)
        else:
            config = ApplicationConfig.load(config_file_path)

        repository = ProductsRepository(config.database_file_path)
        grabber = WbApiGrabber(repository, config.categories, config.min_discount, config.proxies)

        categories_count = len(config.categories)

        if categories_count == 0:
            Logger.warning("No categories in config file")
        else:
            Logger.info(f"Grabber initialized with {categories_count} categories")

        bot = TgBot(
            admins=config.admins,
            token=config.bot_token,
            grabber=grabber,
            requests_interval=config.requests_interval)

        Logger.info("Application started. Waiting for start command from Telegram...")

        try:
            bot.run()
        except Exception as ex:
            Logger.error(ex)
        finally:
            bot.stop()

    except Exception as ex:
        Logger.error(ex)


if __name__ == '__main__':
    main()
