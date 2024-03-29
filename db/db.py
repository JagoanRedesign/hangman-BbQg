import sqlite3
import logging
from typing import Optional, Union
from config import NAME_DATABASE

logger = logging.getLogger('DB')


class ErrorTableName(Exception):
    pass


class DataBase:
    __slots__ = ['connect', 'cursor']

    def __init__(self):
        self.connect = sqlite3.connect(database=NAME_DATABASE)
        self.cursor = self.connect.cursor()
        logger.debug('Создано новое соединение с БД')

    @staticmethod
    def check_table_name(t_name) -> str:
        """
        Проверяет название таблицы на соответствие типу str. В противном случае вызывает исключение.
        Args:
            t_name: название таблицы
        Return:
            True, если имя таблицы str
        Raise:
            ErrorTableName: некорректное имя таблицы
        """
        if not isinstance(t_name, str):
            raise ErrorTableName(f'Некорректное имя таблицы. Был получен тип: {type(t_name)}, а нужна строка!')
        return t_name

    @staticmethod
    def format_string_to_sql(string: str) -> str:
        """
        Форматирует строку экранируя кавычки.
        :param string: Строка для форматирования

        :return: Отформатированная строка
        """
        return string.replace("'", r"\'").replace(r'"', r'\"')

    @staticmethod
    def prepare_set(d: dict) -> str:
        """
        Преобразует словарь в строку для создания конструкции WHERE

        Args:
            d: словарь, который будет преобразован в строку
        Return:
             строка в формате 'ключ=значение, клич2=значение2...'
        """
        if not isinstance(d, dict):
            raise TypeError("Полученный параметр не является словарем")

        result = ''
        for i, items in enumerate(d.items()):
            key, value = items
            if i != 0:
                result += ', '

            result += f'{key}='
            if isinstance(value, str):
                result += f"'{value}'"
            else:
                result += f'{value}'
        return result

    @staticmethod
    def prepare_where(d: dict) -> str:
        """
        Преобразует словарь в строку для создания конструкции WHERE

        Args:
            d: словарь, который будет преобразован в строку
        Return:
             строка в формате 'ключ=значение, клич2=значение2...'
        """
        if not isinstance(d, dict):
            raise TypeError("Полученный параметр не является словарем")

        result = ''
        for i, items in enumerate(d.items()):
            key, value = items
            if i != 0:
                result += ' AND '

            result += f'{key}='
            if isinstance(value, str):
                result += f"'{value}'"
            else:
                result += f'{value}'
        return result

    @staticmethod
    def prepare_insert(d: dict) -> str:
        """
        Преобразует словарь в строку для вставки или обновления данных в таблице

        Args:
            d: словарь, который будет преобразован в строку
        Return:
             строка в формате (ключ, ключ2...) VALUES(значение1, значение2...)'
        """
        if not isinstance(d, dict):
            raise TypeError("Полученный параметр не является словарем")

        result_keys = ''
        result_values = ''
        for i, items in enumerate(d.items()):
            key, value = items
            if i != 0:
                result_keys += ', '
                result_values += ', '

            result_keys += f'{key}'
            if isinstance(value, str):
                result_values += f"'{value}'"
            elif value is None:
                result_values += f'NULL'
            else:
                result_values += f'{value}'
        return f'({result_keys}) VALUES({result_values})'

    @staticmethod
    def prepare_select(data: Union[tuple, list, str]) -> str:
        """
        Преобразует список или кортеж в строку состоящую из элементов исчесляемого типа разделенных запятой.
        Если входящий параметр уже является строкой, то просто возвращает его.
        Используется для запосов в БД после ключевого слова WHERE и для получения списка значений SELECT.

        Args:
            data: данные для подготовки в строку
        Return:
            подготовленная безопасная строка для запроса в БД
        """
        # проверяем where на корректность
        if not isinstance(data, (tuple, str, list)):
            raise TypeError("Неверный тип данных. Входящий параметр должен быть списком, кортежом или строкой!")

        if isinstance(data, (tuple, list)):
            data = ', '.join(f'{element}' for element in data)

        return data

    def insert(self, table: str, data: dict) -> int:
        """
        Вставляет новою запись в указанную таблицу table.
        Args:
            table: таблица, куда нужно вставить запись
            data: данные, которые необходимо занести в таблицу
        Return:
             int: целочисленный идентификатор вставленного элемента
        """
        self.check_table_name(table)
        data = self.prepare_insert(data)

        query = f'INSERT INTO `{table}`{data}'
        logger.debug(f"INSERT: '{query}'")
        res = self.cursor.execute(query)
        self.connect.commit()
        return res.lastrowid

    def select(
            self,
            table: str,
            select_data: Union[list, tuple, str] = '*',
            where: Union[dict, str, None] = None,
            need_all_rows: bool = False)\
            -> list:
        """
        Выполняем SELECT.
        Возвращает значение из таблицы, если оно было найдено или None, если не были найдены нужные значения.
        Args:
            table: название таблицы
            select_data: значения, которые необходимо взять. По умолчанию * - все
            where: условие WHERE
            need_all_rows: нужны ли все строки (True) или только одна (False - по умолчанию)
        Return:
             list: данные из таблицы
        """

        query = f'SELECT'
        self.check_table_name(table)

        # Преобразуем список значений, которые нужно взять из таблицы в строку
        select_data = self.prepare_select(select_data)

        query += f' {select_data} FROM `{table}`'

        # если есть конструкция  WHERE
        if where:
            where = self.prepare_where(where)
            query += ' WHERE ' + where

        logger.debug(f"SELECT: '{query}'")
        self.cursor.execute(query)

        if need_all_rows:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()

    def update(self, table: str, data: Union[dict, str], where: Union[dict, str, None] = None):
        """
        Обновляет данные в таблице согласно заданным параметрам.

        Args:
            table: название таблицы
            data: данные, которые необходимо обновить
            where: условие WHERE, которое показывает, какие строки нужно обновить
        """
        query = f'UPDATE `{self.check_table_name(table)}` SET ' \
                f'{self.prepare_set(data)}'

        # если есть конструкция  WHERE
        if where:
            where = self.prepare_where(where)
            query += " WHERE " + where

        logger.debug(f"UPDATE: '{query}'")
        self.cursor.execute(query)
        self.connect.commit()

    def __del__(self):
        """
        Удаляет соединение с БД и сам экземляр класса.
        """
        self.connect.close()
        logger.debug('Соединение с БД было закрыто')
        del self

    def get_free_select_execute(self, query: str):
        """
        Реализует любой SQL-запрос

        Args:
            query (str): sql-запрос
        """
        return self.cursor.execute(query)
