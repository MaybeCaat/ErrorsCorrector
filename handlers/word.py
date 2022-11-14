from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
import app_logger

import time
import enchant
import requests
import difflib
from bs4 import BeautifulSoup


# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
logger = app_logger.get_logger(__name__)


# стартовое сообщение
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для проверки орфографии. Введите слово и бот выдаст его правильное написание")


# функция для вывода клавиатуры с возможными вариантами
async def get_word(message: types.Message):
    # TODO: проверка на то, что ввели дичь (например, только точку)
    # проверка, что слово изначально правильно написано
    if dictionary.check(message.text):
        await message.reply('Вы правильно написали слово!')
        logger.info('--------------------------------------------------------')
        logger.info(f'Слово: {message.text}')
        logger.info('Написано правильно')
        return
    # проверка на то, что вариантов не найдёт
    if not dictionary.suggest(message.text):
        # TODO: если слово не найдено - попробовать лемматизировать в нач. форму и уже его искать (но хз, работает ли)
        await message.reply('К сожалению, исправления слова не найдены!')
        logger.warning('--------------------------------------------------------')
        logger.warning(f'Слово: {message.text}')
        logger.warning('Исправления не найдены')
        return
    logger.info('--------------------------------------------------------')
    logger.info(f'Слово: {message.text}')
    # получение клавиатуры (отправляем слово в нижнем регистре)
    keyboard = await get_keyboard_corrections(message.text.lower())
    await message.reply(f'Вы ввели слово {message.text}. \nВозможные исправления Вашего слова: ', reply_markup=keyboard)


# исправление слова и возвращение клавиатуры с возможными вариантами
async def get_keyboard_corrections(word):
    start_time = time.time()

    # словарь с значениями степеней сходства изменённого и исходного слова (от 0 до 1)
    sim = dict()
    # получение множества с возможными исправлениями
    # TODO: Пофиксить некоторые элементы в списке изменённых слов
    #   (когда в элементе 2 непонятных слова через пробел + непонятные слова)
    corr_words = set(dictionary.suggest(word))
    for corr_word in corr_words:
        # получаем значение сходства
        measure = difflib.SequenceMatcher(None, word, corr_word).ratio()
        # заносим в виде - слово: значение
        sim[corr_word] = measure
    # сортируем по значению сходства
    sim = dict(sorted(sim.items(), key=lambda x: x[1]))
    # список со всеми исправленными словами в порядке убывания значений их сходства
    corr_words = list(reversed(sim))
    # TODO: проверить новую генерацию списков (лучше ли старой)

    # создаем кнопки
    buttons = [
        types.InlineKeyboardButton(text=el, callback_data=f"word_{el}") for el in corr_words
    ]
    # row_width=1 - одна кнопка в строчке
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    end_time = time.time()
    logger.info(f'Старый список: {dictionary.suggest(word)}')
    logger.info(f'Новый список: {corr_words}')
    logger.info(f'Время исправления слова: {end_time - start_time} секунд')
    return keyboard


# хэндлер на выбор одного из скорректированных слов
async def callbacks_corr_word(call: types.CallbackQuery):
    # извлекаем слово из callback_data (формат: word_слово)
    word = call.data.split("_")[1]
    # получаем правило с помощью get_rule()
    rule = await get_rule(word)
    await call.message.answer(f'Правильное написание: {word} \nПравило: {rule}')
    # отчитываемся о получении колбэка
    await call.answer()


# получение правила на слово
async def get_rule(word):
    start_time = time.time()

    # TODO: очень много правил не находит (нет на сайте таких слов, как шикарно, не повезло и др.)
    # изначальное значение, выведет его, если не найдёт соответствия в цикле
    rule = 'к сожалению, правило не найдено'
    response = requests.get(
        'https://gramotei.online/how-to-spell',
        params={'keyword': word}
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    # проверка, если правило на сайте не найдено
    if soup.blockquote:
        logger.warning('--------------------------------------------------------')
        logger.warning(f'Слово: {word}')
        logger.warning(f'Правило не найдено')
        return rule
    # берём все слова
    word_rows = soup.find_all("div", class_='col-xs-12 col-sm-4 border-bottom search-item')
    for row in word_rows:
        # ищем нужное слово
        if row.a.text == word:
            rule = row.small.text.lower()

    end_time = time.time()
    logger.info('--------------------------------------------------------')
    logger.info(f'Слово: {word}')
    logger.info(f'Правило: {rule}')
    logger.info(f'Время поиска правила: {end_time - start_time} секунд')
    return rule


def register_handlers_word(dp: Dispatcher):
    logger.warning('Module "word" is running')
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(get_word)
    dp.register_callback_query_handler(callbacks_corr_word, Text(startswith="word_"))
