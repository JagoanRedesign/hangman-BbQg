from user import User
from aiogram.types import Message, CallbackQuery


def get_user(func, *args, **kwargs):
    async def wrapper(message: Message):
        user = User(message=message)
        await func(message, user, *args, **kwargs)
    return wrapper


def get_user_by_callback(func, *args, **kwargs):
    async def wrapper(callback: CallbackQuery):
        user = User(callback=callback)
        await func(callback, user, *args, **kwargs)
    return wrapper
