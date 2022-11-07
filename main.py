import difflib
import time
import logging
import enchant
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from config import BOT_TOKEN
from bs4 import BeautifulSoup


# Если слово не найдено - попробовать лематизировать в нач. форму и проверить на правило
# Проверка если введены лишние символы (по типу / убрать, а _ заменить на любую букву (надо протестить)
# Пофиксить некоторые элементы в списке изменённых слов
# (когда в элементе 2 непонятных слова через пробел + непонятные слова)
# Возможно запилить поддержку предложений
# Проверить новую генерацию списков (если что убрать)
# РЕФАКТОР НАЗВАНИЙ ПЕРЕМЕННЫХ


# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# исправление слова и возвращение клавиатуры с возможными вариантами
async def get_keyboard_corrections(word):
    start_time = time.time()

    # словарь с значениями степеней сходства изменённого и исходного слова (от 0 до 1)
    sim = dict()
    # получение множества с возможными исправлениями
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

    # создаем кнопки
    buttons = [
        types.InlineKeyboardButton(text=el, callback_data=f"word_{el}") for el in corr_words
    ]
    # row_width=1 - одна кнопка в строчке
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    end_time = time.time()
    print(f'Старый список: {dictionary.suggest(word)}')
    print(f'Новый список: {corr_words}')
    print(f'Время исправления слова: {end_time - start_time} секунд')
    print('--------------------------------------------------------')
    return keyboard


# получение правила на слово
async def get_rule(word):
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
        return rule
    # берём все слова
    word_rows = soup.find_all("div", class_='col-xs-12 col-sm-4 border-bottom search-item')
    for row in word_rows:
        # ищем нужное слово
        if row.a.text == word:
            rule = row.small.text.lower()

    end_time = time.time()
    print(f'Слово: {word}')
    print(f'Правило: {rule}')
    print(f'Время поиска правила: {end_time - start_time} секунд')
    print('--------------------------------------------------------')
    return rule


# стартовое сообщение
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для проверки орфографии. Введите слово и бот выдаст его правильное написание")


# функция для вывода клавиатуры с возможными вариантами
@dp.message_handler()
async def get_word(message: types.Message):
    # проверка, что слово изначально правильно написано
    if dictionary.check(message.text):
        await message.reply('Вы правильно написали слово!')
        print(f'Слово: {message.text}')
        print('Написано правильно')
        print('--------------------------------------------------------')
        return
    # проверка на то, что вариантов не найдёт
    if not dictionary.suggest(message.text):
        await message.reply('К сожалению, исправления слова не найдены!')
        print(f'Слово: {message.text}')
        print('Исправления не найдены')
        print('--------------------------------------------------------')
        return
    print(f'Слово: {message.text}')
    # получение клавиатуры (отправляем слово в нижнем регистре)
    keyboard = await get_keyboard_corrections(message.text.lower())
    await message.reply(f'Вы ввели слово {message.text}. \nВозможные исправления Вашего слова: ', reply_markup=keyboard)


# хэндлер на выбор одного из скорректированных слов
@dp.callback_query_handler(Text(startswith="word_"))
async def callbacks_corr_word(call: types.CallbackQuery):
    # извлекаем слово из callback_data (формат: word_слово)
    word = call.data.split("_")[1]
    # получаем правило с помощью get_rule()
    rule = await get_rule(word)
    await call.message.answer(f'Правильное написание: {word} \nПравило: {rule}')
    # отчитываемся о получении колбэка
    await call.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
