from typing import Union
from db.db import DataBase
from io import BufferedReader


def get_image(image: Union[str, BufferedReader]):
    """
    Получает идентификатор фото для отправки сообщения

    Args:
        image: расположение файла с изображением
    """
    db = DataBase()
    file_id = db.select(table='photo', select_data='file_id', where={'photo': image})
    if file_id:
        # если есть, берем идентификатор изображения
        photo = file_id[0]
    else:
        # если нет, берем изображение из файла
        photo = open(image, mode='rb')
    return photo
