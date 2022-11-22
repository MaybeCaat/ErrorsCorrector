import string
import app_logger
import time
import enchant
import requests
from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.callback_data import CallbackData
from pymorphy2 import MorphAnalyzer
from config import BOT_TOKEN
from bs4 import BeautifulSoup

# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
logger = app_logger.get_logger(__name__)
morph = MorphAnalyzer()
cb = CallbackData('post', 'old_word', 'word')
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# TODO: возможно запилить поддержку предложений (и словосочетаний с значением, например пре-, при-)
# TODO: сделать красивое оформление
# убрать кнопки клавиатуры с пробелами (c хернёй, а с НЕ не убирать)
# попробовать переводить в другую часть речи, если не находит правило


# стартовое сообщение
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! \n"
                         "Перед вами бот для проверки орфографии. \n\n"
                         "Введите слово и бот выдаст: \n"
                         "1) <i>правильное написание</i> слова \n"
                         "2) <i>правило</i>, которое использовалось в данном случае")


# функция для вывода клавиатуры с возможными вариантами
@dp.message_handler()
async def get_word(message: types.Message):
    # проверка, что строка состоит только из символов (НЕТ букв и цифр)
    isOnlySymbols = all(symb in string.punctuation for symb in message.text)
    if isOnlySymbols is True:
        await message.reply('Пожалуйста, введите <u>слово</u>, а не набор символов!')
        logger.warning('--------------------------------------------------------')
        logger.warning(f'Слово: {message.text}')
        logger.warning('Введены только символы')
        return
    # проверка, что ввели несколько слов
    if len(message.text.split()) != 1:
        await message.reply('Пожалуйста, введите <u>ОДНО</u> слово!')
        logger.warning('--------------------------------------------------------')
        logger.warning(f'Слова: {message.text}')
        logger.warning('Введено несколько слов')
        return
    # проверка, что слово изначально правильно написано
    if dictionary.check(message.text):
        await message.reply('Вы <u>правильно</u> написали слово!')
        logger.info('--------------------------------------------------------')
        logger.info(f'Слово: {message.text}')
        logger.info('Написано правильно')
        return
    # проверка на то, что вариантов не найдёт
    if not dictionary.suggest(message.text):
        await message.reply('К сожалению, исправления слова <u>не найдены</u>!')
        logger.warning('--------------------------------------------------------')
        logger.warning(f'Слово: {message.text}')
        logger.warning('Исправления не найдены')
        return
    logger.info('--------------------------------------------------------')
    logger.info(f'Слово: {message.text}')
    # получение клавиатуры (отправляем слово в нижнем регистре)
    keyboard = await get_keyboard_corrections(message.text.lower())
    await message.reply(f'Вы ввели слово <i>{message.text}</i>. \nВарианты возможных исправлений Вашего слова: ',
                        reply_markup=keyboard)


# исправление слова и возвращение клавиатуры с возможными вариантами
async def get_keyboard_corrections(word):
    start_time = time.time()

    # список со всеми исправленными словами
    corr_words = dictionary.suggest(word)
    # создаем кнопки
    buttons = [
        types.InlineKeyboardButton(text=el, callback_data=cb.new(old_word=word, word=el)) for el in corr_words
    ]
    # row_width=1 - одна кнопка в строчке
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    end_time = time.time()
    logger.info(f'Список исправлений: {corr_words}')
    logger.info(f'Время исправления слова: {end_time - start_time} секунд')
    return keyboard


# хэндлер на выбор одного из скорректированных слов
@dp.callback_query_handler(cb.filter())
async def callbacks_corr_word(call: types.CallbackQuery, callback_data: dict):
    # извлекаем изначальное и скорректированное слово
    old_word = callback_data['old_word']
    word = callback_data['word']
    # получаем правило с помощью get_rule()
    rule = await get_rule(old_word, word)
    await call.message.answer(f'Правильное написание: <i>{word}</i> \n'
                              f'<i>Правило</i>, по которому написано слово: {rule}')
    # отчитываемся о получении колбэка
    await call.answer()


# получение правила на слово
async def get_rule(old_word, word):
    start_time = time.time()

    # изначальное значение, выведет его, если не найдёт соответствия в цикле
    rule = 'к сожалению, правило не найдено'
    response = requests.get(
        'https://gramotei.online/how-to-spell',
        params={'keyword': word}
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    # проверка, если правило на сайте не найдено
    if soup.blockquote:
        # лемматизируем слово
        word = morph.normal_forms(word)[0]
        response = requests.get(
            'https://gramotei.online/how-to-spell',
            params={'keyword': word}
        )
        soup = BeautifulSoup(response.text, 'html.parser')

    # если всё равно слово не найдено
    if soup.blockquote:
        word = morph.normal_forms(old_word)[0]
        response = requests.get(
            'https://gramotei.online/how-to-spell',
            params={'keyword': word}
        )
        soup = BeautifulSoup(response.text, 'html.parser')

    # и всё равно не найдено
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
            break

    end_time = time.time()
    logger.info('--------------------------------------------------------')
    logger.info(f'Слово: {word}')
    logger.info(f'Правило: {rule}')
    logger.info(f'Время поиска правила: {end_time - start_time} секунд')
    return rule


if __name__ == '__main__':
    logger.warning('Bot started')
    executor.start_polling(dp, skip_updates=True)
    logger.warning('Bot stopped')
