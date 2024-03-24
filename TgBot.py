import time
import telebot
from Logger import Logger
from TgProductInfo import TgProductInfo
from WbApiGrabber import WbApiGrabber
from threading import Thread, Event


class TgBot:
    def __init__(self,
                 admins: list[str],
                 token: str,
                 grabber: WbApiGrabber,
                 requests_interval: float):
        self.__admins = admins
        self.__grabber = grabber
        self.__requests_interval = requests_interval
        self.__chat_id = 0
        self.__md_chars = '.|-()'
        self.__started = False
        self.__event = Event()
        bot = telebot.TeleBot(token)

        bot.set_my_commands([
            telebot.types.BotCommand("/start", "start"),
        ])

        @bot.message_handler(commands=['start'])
        def start_command(message: telebot.types.Message) -> None:
            user = message.from_user.username

            self.__chat_id = message.chat.id
            Logger.info(f'User "{user}" sent start command in chat "{message.chat.title}"')

            if user not in self.__admins:
                Logger.warning(f'User "{user}" is not admin. Bot is not running')
                self.__bot.reply_to(message, "You are not my admin")
                return

            if self.__started:
                Logger.warning('Bot already started')
                return

            self.__event.clear()
            self.__thread.start()
            self.__started = True
            Logger.info('Bot started')

        self.__bot = bot
        self.__thread = Thread(target=self.__update_products_info)

    def run(self):
        self.__bot.infinity_polling()

    def stop(self) -> None:
        Logger.info('Stopping bot...')
        self.__event.set()

        if self.__started:
            self.__thread.join()

        self.__bot.stop_bot()
        self.__started = False

        Logger.info('Bot successfully stopped')

    def __update_products_info(self):
        while not self.__event.is_set():
            try:
                start = time.time()
                products = self.__grabber.get_products_at_discount(self.__event)

                for product in products:
                    while not self.__event.is_set():
                        try:
                            self.__send_product_info(product)
                            break
                        except Exception as e:
                            Logger.warning(e)
                            parts = str(e).split('after ')

                            if len(parts) == 2 and parts[1].isnumeric():
                                sleep = float(parts[1]) + 1
                                Logger.info(f'Waiting for {sleep} seconds')
                                time.sleep(sleep)

                diff = time.time() - start

                if diff < self.__requests_interval:
                    time.sleep(self.__requests_interval - diff)
            except Exception as e:
                Logger.error(e)

    def __replace_md_characters(self, data) -> str:
        string = str(data)

        for char in self.__md_chars:
            string = string.replace(char, '\\' + char)

        return string

    def __send_product_info(self, info: TgProductInfo):
        name = self.__replace_md_characters(info.name)
        current_price = self.__replace_md_characters(info.current_price / 100)
        old_price = self.__replace_md_characters(info.old_price / 100)
        discount = self.__replace_md_characters(round(info.discount, 2))
        min_price = self.__replace_md_characters(info.price_history.min_price / 100)
        max_price = self.__replace_md_characters(info.price_history.max_price / 100)

        self.__bot.send_photo(
            chat_id=self.__chat_id,
            photo=info.photo_url,
            parse_mode='MarkdownV2',
            caption=f"""📉*{current_price}₽* ~{old_price}₽~
🛍{name}

🔥Скидка: *\\-{discount}%*
🏢Склад: *{info.store} \\- {info.in_stock} шт*
↔️Диапазон: *{min_price}₽ \\- {max_price}₽*
📏Размеры: *{info.sizes}*

⭐️{self.__replace_md_characters(info.rating)}\\|📝{info.reviews}

[К товару]({info.product_url})
""")
