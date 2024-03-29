from typing import Optional, Union

from db.db import DataBase
import logging
from aiogram.types import Message, User as TUser, CallbackQuery
import notification
import asyncio

logger = logging.getLogger('User')


class CreatingUserException(Exception):
    pass


class UserNotFound(Exception):
    pass


class User:
    __slots__ = ['user_id', 'name', 'db', 'referer']

    def __init__(
            self,
            user_id: Union[int, str, None] = None,
            message: Optional[Message] = None,
            user: Optional[TUser] = None,
            callback: Optional[CallbackQuery] = None
    ):
        """
        Инициализация пользователя.

        Args:
            user_id: пользовательский user_id в телеграм.
            message: объект типа message, из которого можно будет получить данные об отправителе
            user: объект типа user от aiogram
        """
        if user_id is None and message is None and user is None and callback is None:
            raise CreatingUserException("Не задан ни один параметр для инициализации")

        if not isinstance(user_id, (str, int)) and not isinstance(message, Message) \
                and not isinstance(user, User) and not isinstance(callback, CallbackQuery):
            raise CreatingUserException("Неверный тип параметра для инициализации")

        # проверяем, какой из аргументов был предоставлен для инициализации
        if user_id:
            self.user_id = int(user_id)

        elif message:
            self.user_id = message.from_user.id
            self.name = message.from_user.full_name

        elif callback:
            self.user_id = callback.from_user.id
            self.name = callback.from_user.full_name

        elif user:
            self.user_id = user.id
            self.name = user.full_name

        # создаем экземпляр класса DateBase, для работы с БД
        self.db = DataBase()

        # проверяем, есть ли пользователь в бд (зарегистрирован ли он) и при необходимости регистрирует его
        self._check_register(message)

    def _check_register(self, message: Optional[Message] = None) -> bool:
        """
        Проверяет, был ли зарегистрирован пользователь. Если нет, регистирирует его

        Args:
            message: параметр message из которого можно получить информацию о переходе по реферальной ссылке.

        Return:
             Возвращает True, если пользователь был зарегистрирован и False, если не был.
        """
        user_register = self.db.select(table='user', select_data='name', where={'user_id': self.user_id})

        # если пользователь не зарегистрирован
        if not user_register:
            self.referer = None
            # проверяем, перешел ли пользователь по реферальной ссылке
            if message and message.text.startswith('/start'):
                referer_temp_row = message.text.split()
                if len(referer_temp_row) == 2 and User.check_user_by_id(user_id=referer_temp_row[1]):
                    self.referer = int(referer_temp_row[1])

                    # отправляем уведомление рефоводу о новом реферале
                    asyncio.create_task(
                        notification.new_referal(user_referer_id=referer_temp_row[1], name_referal=self.name))

            # регистрируем пользователя
            self.db.insert('user', {'user_id': self.user_id, 'name': self.name, 'referer': self.referer})

            logger.info(f'Новый пользователь! Имя: {self.name}; '
                        f'user_id: {self.user_id}; referer: {self.referer}')

            # пользователь не был зарегистрирован
            return False

        # пользователь был зарегистрирован. Берем данные из БД
        self._get_data_from_db()
        return True

    def _get_data_from_db(self):
        """
        Получаем данные из бд.
        Проверяем, необходимо ли зарегистрировать пользователя или обновить имя пользователя в БД.
        """
        select = self.db.select(table='user', select_data=['name', 'referer'], where={'user_id': self.user_id})

        # проверяем найден ли пользователь
        if not select:
            raise UserNotFound('Пользователь не был найден')

        # проверяем имя на сходство
        if not self.name:
            # если имя пользователя пустое, то берем информацию в БД
            self.name = select[0]
        elif self.name and self.name != select[0]:
            # если у пользователя новое имя, обновляем его в БД
            self._update_name()

        # берем информацию о реферере
        self.referer = select[1]

    def _update_name(self):
        """
        Обновляет имя пользователя в БД

        """
        self.db.update(table='user', data={'name': self.name}, where={'user_id': self.user_id})

    @staticmethod
    def check_user_by_id(user_id: Union[int, str]) -> bool:
        """
        Проверяет был ли зарегистрирован пользователь с указанным user_id
        Args:
            user_id: уникальный идентификатор пользователя в Telegram

        Return:
            True - пользователь зарегистрирован; False - не зарегистрирован
        """
        if not isinstance(user_id, (str, int)):
            raise ValueError('Неверный тип данных')
        user_id = int(user_id)
        db = DataBase()
        select = db.select(table='user', where={'user_id': user_id})
        return True if select else False
