from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from image import get_image
from text import text
from handlers import handler_decorates
from user import User
from aiogram.types import ReplyKeyboardMarkup, InputMediaPhoto
from config import BOT_USERNAME
from text.string_formatter_mb import format_string
from game import Game
from db.db import DataBase
from io import BufferedReader


async def send_photo(
        message: Message, caption: str,
        photo: (str, BufferedReader),
        keyboard: (InlineKeyboardMarkup, ReplyKeyboardMarkup)) -> bool:
    """
    Отправляет сообщение с изображением и при необходимости кэширует его

    :param message:
    :param caption: текст под изображением
    :param photo: изображение
    :param keyboard: клавиатура
    :return: True - отправка удалась, False - ошибка
    """
    try:
        sent = await message.answer_photo(caption=caption, reply_markup=keyboard, photo=photo)
    except:
        return False
        pass
    else:
        cashing_photo(photo, sent)
    return True


async def edit_media(
        message: Message, caption: str,
        photo: (str, BufferedReader),
        keyboard: (InlineKeyboardMarkup, ReplyKeyboardMarkup) = None) -> bool:
    """
    Отправляет сообщение с изображением и при необходимости кэширует его

    :param message:
    :param caption: текст под изображением
    :param photo: изображение
    :param keyboard: клавиатура
    :return: True - отправка удалась, False - ошибка
    """
    media = InputMediaPhoto(media=photo, caption=caption)
    try:
        sent = await message.edit_media(media=media, reply_markup=keyboard)
    except Exception as e:
        print(e)
        return False
    else:
        cashing_photo(photo, sent)
    return True


def cashing_photo(photo, sent) -> bool:
    """
    Кэширует изображение в базе данных
    :param photo:
    :param sent: отправленное сообщение с фото
    :return: True - кэширование удалось, False - переданный тип изображение не является строкой.
    """
    if not isinstance(photo, str):
        db = DataBase()
        select = db.select(table='photo', where={'file_id': sent.photo[0].file_id})
        if not select:
            db.insert(table='photo', data={'photo': photo.name, 'file_id': sent.photo[0].file_id})
        return True
    return False


@handler_decorates.get_user
async def start_game(message: Message, user: User):
    """
    Запуск игры. Присылает пользователю игру.

    :param message: сообщение
    :param user: пользователь, отправивший сообщение
    :return: None
    """
    game = Game(user)
    msg, keyboard, photo = game.get_game_content()
    await send_photo(message=message, caption=msg, keyboard=keyboard, photo=photo)


@handler_decorates.get_user
async def show_records(message: Message, user: User):
    db = DataBase()
    my_point = db.select(table='games', select_data='sum(point)', where={'user_id': user.user_id})[0]
    my_point = my_point if my_point else 0
    msg = f'*{text.main_menu[1]}*' \
          f'\n\n У вас: *{my_point}* 💎 очков\n'

    row_record = db.get_free_select_execute(
        'SELECT sum(games.point), user.name '
        'FROM games LEFT JOIN user ON user.user_id = games.user_id '
        'GROUP BY games.user_id ORDER BY sum(games.point) DESC LIMIT 50 ')

    for i, one_record in enumerate(row_record, 1):
        msg += f'\n{i}\. {format_string(one_record[1])} \- *{one_record[0]}* 💎'
    await message.answer(msg)


@handler_decorates.get_user
async def call_friends(message: Message, user: User):
    """
    Присылает пользователю сообщение с его рефеальной ссылкой

    :param message: сообщение пользователя
    :param user: пользователь
    :return: None
    """
    link = format_string(f"https://t.me/{BOT_USERNAME}?start={str(user.user_id)}")
    msg = 'Вы можете пригласить своих друзей в игру виселица' \
          '\nДля этого посто отправьте им ссылку: ' \
          f'\n\n{link}'
    await message.answer(msg)


@handler_decorates.get_user
async def get_another_message(message: Message, *args, **kwargs):
    """
    Сообщение, которое реагирует на нажатие любых клавиш кроме кнопок на клавиатуре.
    Также, вызывается командой /start.

    :param message: сообщение пользователя
    :param args:
    :param kwargs:
    :return: None
    """
    msg = f'*Добро пожаловать в игру ☠️ виселица\!*' \
          f'\n\nВаша задача в игре угадывать слова, делая как можно меньше ошибок\.' \
          f'\nНажимай *☠️ играть*, чтобы начать\!'

    keyboard = ReplyKeyboardMarkup()
    keyboard.resize_keyboard = True
    keyboard.row_width = 2
    keyboard.add(*text.main_menu)

    photo = get_image('image/hangman.png')

    await send_photo(message=message, photo=photo, caption=msg, keyboard=keyboard)


@handler_decorates.get_user_by_callback
async def press_button(callback: CallbackQuery, user: User):
    if Game.isCreatedGame(user):

        game = Game(user=user)
        code, ntf = game.press_button(callback.data)
        try:
            # по идее, здесь можно выводить уведомление ntf, но оно мешает игре
            await callback.answer()
        except:
            pass

        msg, keyboard, photo = game.get_game_content()
        if code == -2:
            await edit_media(message=callback.message, photo=photo, caption=msg)
        elif code == -1:
            await edit_media(message=callback.message, photo=photo, caption=msg, keyboard=keyboard)
        elif code == 1:
            await callback.message.edit_caption(caption=msg, reply_markup=keyboard)
        elif code == 2:
            await callback.message.edit_caption(caption=msg)


    else:
        await callback.answer('Нет найденных игр')
