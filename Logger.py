from datetime import datetime
import colorama
from colorama import Fore

colorama.init()


class Logger:
    @staticmethod
    def info(message: str = None):
        print(Fore.LIGHTBLUE_EX + f"[Info    {Logger.__get_time()}] - {message}" + Fore.RED)

    @staticmethod
    def error(message: str | Exception = None):
        print(Fore.RED + f"[Error   {Logger.__get_time()}] - {message}" + Fore.RED)

    @staticmethod
    def warning(message: str | Exception = None):
        print(Fore.YELLOW + f"[Warning {Logger.__get_time()}] - {message}" + Fore.RED)

    @staticmethod
    def __get_time() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
