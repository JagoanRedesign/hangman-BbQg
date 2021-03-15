import logging
from handlers import handler
from aiogram import Dispatcher
from text import text

logger = logging.getLogger('Handler registrator')


def register_handlers(dp: Dispatcher) -> True:
    """
    Регистрирует все хэндлеры для отлова сообщений

    :param dp:
    :return:
    """
    dp.register_message_handler(callback=handler.start_game, regexp=text.main_menu[0])
    dp.register_message_handler(callback=handler.show_records, regexp=text.main_menu[1])
    dp.register_message_handler(callback=handler.call_friends, regexp=text.main_menu[2])
    dp.register_callback_query_handler(callback=handler.press_button)
    dp.register_message_handler(callback=handler.get_another_message)

    # логируем успешную регистрацию хэндлеров
    logger.info('All handlers war registered!')
    return True
