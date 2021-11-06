# main.py
# !/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from aiogram import Bot, Dispatcher, executor
from config import TOKEN
from handlers.handler_registrator import register_handlers

# подключаем логирование
logging.basicConfig(level=logging.DEBUG)

# создаем бота и диспатчер
bot = Bot(token=TOKEN, parse_mode='MarkdownV2')
dp = Dispatcher(bot=bot)


def main():
    """
    Стартовая функция. Запускает наш проект
    Запускает регистрацию хэндлеров.
    Запускает пуллинг.
    """
    register_handlers(dp)
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
