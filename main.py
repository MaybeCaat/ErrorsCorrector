import difflib
import time
import logging
import enchant
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from config import BOT_TOKEN
from bs4 import BeautifulSoup

# Если слово не найдено - попробовать лематизировать в нач. форму и проверить на правило (проверить, будет ли находить)
# Пофиксить некоторые элементы в списке изменённых слов
# (когда в элементе 2 непонятных слова через пробел + непонятные слова)
# Возможно запилить поддержку предложений (и словосочетаний с значением, например пре-, при-)
# Проверить новую генерацию списков (если что убрать)
# СДЕЛАТЬ КРАСИВОЕ ОФОРМЛЕНИЕ
# возможно разделить на файлы (тогда и логи разделить)
# проверка, когда ввели чушь (например, только точку)
# очень много не находит правил (шикарно, не повезло)
# СДЕЛАТЬ ЛОГИ В КОНСОЛЬ (включение бота)
# ДОПИСАТЬ README.md


# не забыть перекинуть файлы локализации
dictionary = enchant.Dict('ru_RU')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs.log', 'w', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


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
        logger.info('--------------------------------------------------------')
        logger.info(f'Слово: {message.text}')
        logger.info('Написано правильно')
        return
    # проверка на то, что вариантов не найдёт
    if not dictionary.suggest(message.text):
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
    logger.info(f'Старый список: {dictionary.suggest(word)}')
    logger.info(f'Новый список: {corr_words}')
    logger.info(f'Время исправления слова: {end_time - start_time} секунд')
    return keyboard


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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
