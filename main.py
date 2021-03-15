# main.py
# !/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from aiogram import Bot, Dispatcher, executor
from config import TOKEN
from handlers.handler_registrator import register_handlers

# подключаем логирование
# рекомендуется уровень логиование: INFO
# f_handler = logging.FileHandler(filename='log.txt', mode="w", encoding='utf-8')
#
# logging.Handler = f_handler
# f_format = logging.Formatter('%(asctime)s - %(message)s')
# f_handler.setFormatter(f_format)
# logging.getLogger().addHandler(f_handler)

logging.basicConfig(level=logging.DEBUG)

# создаем бота и диспатчер
bot = Bot(token=TOKEN, parse_mode='MarkdownV2')
dp = Dispatcher(bot=bot)


def main():
    """
    Стартовая функция. Запускает наш проект
    Запускает регистрацию хэндлеров.
    Запускает пуллинг.

    :return:
    """
    register_handlers(dp)
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
