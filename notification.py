from typing import Union
from config import TOKEN
from aiogram import Bot
from text.string_formatter_mb import format_string


async def new_referal(user_referer_id: Union[int, str], name_referal: str) -> bool:
    """
    Отправляет уведомление о регистрации нового реферала

    Args:
        user_referer_id: идентификатор реферера
        name_referal: имя реферала
    Return:
        флаг сигнализирующий об успешности отправки уведомления о регистрации нового реферала
    """
    bot = Bot(token=TOKEN, parse_mode='MarkdownV2')
    try:
        msg = '👋 По вашей реферальной ссылке зарегистрировался новый участник\n\n' \
              f'*{format_string(name_referal)}*'
        await bot.send_message(chat_id=user_referer_id, text=msg)
        res = True
    except:
        res = False
    await bot.close()
    return res

