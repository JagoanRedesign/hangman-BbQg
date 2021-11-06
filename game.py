from typing import Union, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from user import User
from db.db import DataBase
from random import randint
from time import time
from io import BufferedReader


class Game:
    __slots__ = ['db', 'select', 'lost_health', 'word_id', 'time_start', 'input_letters', 'word_array', 'category_id',
                 'word', 'category', 'user', 'status', 'point']

    def __init__(self, user: User):
        """
        Инициализирует объект игры. Берет уже созданную игру из БД или создает новую и помещает ее в БД.

        Args:
             user: данные о пользователе
        """
        # пользователь
        self.user = user

        # создаем соединение с БД
        self.db = DataBase()

        # запрашивает информацию о существующей игре
        select = Game.exist_created_games(self.user)

        # выбранные буквы пользователем
        self.input_letters = ''

        # уже имеется созданная игра
        if select:
            # оставшиеся жизни
            self.lost_health = select[0]
            # id слова в базе
            self.word_id = select[1]
            # время начала игры
            self.time_start = select[2]

            # выбранные буквы пользователь, если значение не пустое, то берем его
            if select[3]:
                self.input_letters = select[3]

        # нет созданной игры
        else:
            # берем общее количество слов в базе
            count_words = self.db.select(table='words', select_data='count(*)')[0]
            # генерируем рандомное число от 1 до количества слов. Это будет наш идентификатор слова
            self.word_id = randint(1, count_words)
            # количество жизней по умолчанию 7
            self.lost_health = 7
            # время начала игры - сейчас
            self.time_start = time()
            # вставляем информацию об игре в БД
            self.db.insert(
                table='games', data={'word_id': self.word_id, 'time_start': self.time_start, 'user_id': user.user_id})

        # нужно по указанному ID слово, получить само слово и его категорию. Делаем соответствующий запрос
        self.word_array = self.db.select(table='words', select_data=['cat_id', 'name'], where={'id': self.word_id})
        # получаем ID категории и само слово
        self.category_id, self.word = self.word_array

        # делаем все буквы в слово большими, так как все сравнение в игре будет идти с большими буквами
        self.word = self.word.upper().replace('Ё', 'Е')

        # извлекаем название категории из БД
        self.category = self.db.select(table='categories', select_data='name', where={'id': self.category_id})[0]

        # статус игры. 0 - игра идет, -2 игра завершена проигрышем. 2 - победой
        self.status = 0

        # количество очков за игру
        self.point = 0

    def get_game_content(self) -> Tuple[str, InlineKeyboardMarkup, Union[str, BufferedReader]]:
        """
        Получает информацию о статусе игры из БД

        Return:
            возвращает текст с игрой, клавиатуру и фотографию
        """
        # создаем объект с изображением.
        # проверяем, есть ли изображение в кэшэ
        file_id = self.db.select(table='photo',
                                 select_data='file_id',
                                 where={'photo': f'image/{8 - self.lost_health}.png'})
        if file_id:
            # если есть, берем идентификатор изображения
            photo = file_id[0]
        else:
            # если нет, берем изображение из файла
            photo = open(f'image/{8 - self.lost_health}.png', mode='rb')

        if self.status == 0:
            keyboard = self._get_keyboard_for_game()
            word = self._get_word_for_game()
        else:
            word = self.word
            keyboard = None

        msg = f'*Категория:* {self.category}' \
              f'\n\n*Слово:*' \
              f'\n{word}'
        if self.status == -2:
            msg += "\n\n❌ Игра закончена\! Вы проиграли 😔"
        elif self.status == 2:
            msg += "\n\n✅ Победа\!" \
                   f"\n\nВы получили: *{self.point}* 💎 очков"

        return msg, keyboard, photo

    def _get_word_for_game(self):
        word = ''
        for let in self.word:
            if let in self.input_letters:
                word += let
            else:
                word += '◻️'
        return word

    def _get_keyboard_for_game(self) -> InlineKeyboardMarkup:
        """
        Генерирует клавиатуру для игры на основе уже выбираемых букв.
        Помечает их соответствующими маркерами

        Return:
            клавиатура
        """
        # создаем клавиатуру
        keyboard = InlineKeyboardMarkup()
        # устанавливаем ширину 7
        keyboard.row_width = 7
        # будем начинать перечисление с заглавной буквы А
        let_a_number = ord('А')

        # генерируем алфавит в виде списка
        array_alphabet = [chr(num) for num in range(let_a_number, let_a_number + 32)]

        # проходим по каждой букве алфавита
        for let in array_alphabet:
            # если пользователь нажимал на букву
            if let in self.input_letters:
                # если нажатая буква присутсвует в загаданном слове
                if let in self.word:
                    text_button = f'✅{let}'
                # иначе ее нет в слове, значит она неверная
                else:
                    text_button = f'❌{let}'

            # иначе пользователь еще не нажимал букву
            else:
                text_button = f'ᅠ{let}'
                # Вставка происходит весте с невидимым символом, так как иначе получится только один символ на кнопке
                # из-за чего клавиатуру будет не пропорциональной

            # помещаем кнопку в клавиатуру
            button = InlineKeyboardButton(callback_data=f'let:{let}', text=text_button)
            keyboard.insert(button)

        return keyboard

    def press_button(self, button: str) -> Tuple[int, str]:
        """
        Функция, вызываемая при выборе буквы пользователем

        Args:
            button: callback.data кнопки с буквой
        Return:
            int: целочисленный статус информирующий о правильном или неправильном угадывании буквы и о возможности
                 продолжать игру на основе оставшихся жизней.
            str: текстовое обозначение статуса
        """
        # берем букву из кэллбэк-даты (она у нас находится после ':')
        letter = button.split(':')[1]

        # проверяем, нажимал ли пользователь ранее эту букву
        if letter in self.input_letters:
            return 0, 'Вы уже выбирали эту букву'

        # добавляем ее к к списку нажатых букв
        self.input_letters += letter

        # если буква присутствует в загаданном слове
        if letter in self.word:
            # если пользователь отгадал слово полностью
            if set(self.input_letters) >= set(self.word):

                # подсчитываем очки за игру
                self.point += self.lost_health * 25
                time_finish = time()
                time_point = 150 - (time_finish - self.time_start)
                if time_point > 0:
                    self.point += int(time_point)
                # обновляем соотвествующую информацию об игре в БД
                self.db.update(
                    table='games',
                    data={'status': 2, 'input_letters': self.input_letters, 'time_finish': time(), 'point': self.point},
                    where=self._get_where_my_game(self.user))
                self.status = 2
                return 2, 'Слово полностью отгадано!'

            # если слово еще не полность отгадано
            self.db.update(table='games', data={'input_letters': self.input_letters})
            return 1, 'Вы отгадали букву!'

        # если пользователь выбрал букву, которой нет в слове, забираем 1 жизнь
        self.lost_health -= 1
        # если колиечтво жизней осталось 0, пользователь проиграл
        if self.lost_health == 0:
            # завершаем игру
            self.db.update(
                table='games', data={'status': -2, 'input_letters': self.input_letters, 'time_finish': time()},
                where=self._get_where_my_game(self.user))
            self.status = -2
            return -2, 'Неверная буква! Вы проиграли'

        # если жизни еще остались
        self.db.update(
            table='games', data={'input_letters': self.input_letters, 'lost_health': self.lost_health},
            where=self._get_where_my_game(self.user))
        return -1, 'Неверная буква!'

    @staticmethod
    def exist_created_games(user: User) -> Union[list, bool]:
        """
        Функция проверяем, есть ли у пользователя созданные игры.

        Args:
            user: пользователь
        Return:
            False - созданных игр нет; list - с самой игрой иначе
        """
        db = DataBase()
        select = db.select(
            table='games',
            select_data=['lost_health', 'word_id', 'time_start', 'input_letters'],
            where=Game._get_where_my_game(user))
        return select if select else False

    @staticmethod
    def _get_where_my_game(user: User) -> dict:
        """
        Возвращает словарь для запроса в БД для поиска игры

        Args:
            user: пользователь
        Return:
            словарь для запроса WHERE
        """
        return {'user_id': user.user_id, 'status': 0}
