import time
import logging
import enchant
import requests
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from bs4 import BeautifulSoup

# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Исправление слова и засечение времени
async def check_word(word):
    start_time = time.time()

    result_word = dictionary.suggest(word)
    # ЧТОБЫ РАБОТАЛО С РУССКИМИ СЛОВАМИ
    res = requests.get(
        'https://gramotei.online/how-to-spell',
        params={'keyword': result_word[0]}
    )
    soup = BeautifulSoup(res.text, 'html.parser')
    elem = soup.find("div", class_='hidden-xs col-sm-8 border-bottom text-muted search-item')
    rule = elem.text
    result = [result_word, rule]

    end_time = time.time()
    print(f'Время исправления слова: {end_time - start_time} секунд')
    return result


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это бот для проверки орфографии. Введите слово и бот выдаст его правильное написание")


@dp.message_handler()
async def get_word(message: types.Message):
    if dictionary.check(message.text):
        await message.reply('Вы правильно написали слово!')
        return
    result_word = await check_word(message.text)
    await message.reply(f'Правильное написание Вашего слова: {result_word[0]}. \nПравило написания: {result_word[1]}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
