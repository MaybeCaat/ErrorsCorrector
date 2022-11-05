import time
import logging
import enchant
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from config import BOT_TOKEN
from bs4 import BeautifulSoup

# ВОЗМОЖНО СДЕЛАТЬ ЛОГИ
# ПОФИКСИТЬ ВЗЯТИЕ ЭЛЕМЕНТА:
# не всегда на первом месте в сайте нужное


# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Исправление слова и засечение времени
async def get_keyboard_corrections(word):
    start_time = time.time()

    # получение списка с возможными исправлениями
    result_word = dictionary.suggest(word)
    buttons = [
        types.InlineKeyboardButton(text=el, callback_data=f"word_{el}") for el in result_word
    ]
    # row_width=1 - одна кнопка в строчке
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    end_time = time.time()
    print(f'Время исправления слова: {end_time - start_time} секунд')
    return keyboard


# получение правила на слово
async def get_rule(word):
    start_time = time.time()

    res = requests.get(
        'https://gramotei.online/how-to-spell',
        params={'keyword': word}
    )
    soup = BeautifulSoup(res.text, 'html.parser')
    # проверка, если правило на сайте не найдено
    if soup.blockquote:
        return "К сожалению, правило не найдено"
    # поиск элемента с нужным названием
    word_elem = soup.find_all("div", class_='col-xs-12 col-sm-4 border-bottom search-item')
    # изначальное значение, выведет его, если не найдёт соответствия в цикле
    rule = 'К сожалению, правило не найдено'
    # прохожу по всем словам
    for el in word_elem:
        # ищу нужное слово
        if el.a.text == word:
            rule = el.small.text

    end_time = time.time()
    print(f'Время поиска правила: {end_time - start_time} секунд')
    return rule


# стартовое сообщение
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для проверки орфографии. Введите слово и бот выдаст его правильное написание")


@dp.message_handler()
async def get_word(message: types.Message):
    # проверка, что слово изначально правильно написано
    if dictionary.check(message.text):
        await message.reply('Вы правильно написали слово!')
        return
    keyboard = await get_keyboard_corrections(message.text)
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
