from db.db import DataBase
from io import BufferedReader


def get_image(image: (str, BufferedReader)):
    db = DataBase()
    file_id = db.select(table='photo', select_data='file_id', where={'photo': image})
    if file_id:
        # если есть, берем идентификатор изображения
        photo = file_id[0]
    else:
        # если нет, берем изображение из файла
        photo = open(image, mode='rb')
    return photo
