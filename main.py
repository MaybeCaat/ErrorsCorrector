import time
import logging
from aiogram import Bot, Dispatcher, executor, types
from autocorrect import Speller
from config import BOT_TOKEN

spell = Speller('ru', only_replacements=True)
# only_replacements - ищет только замены букв в слове, нет пропуска букв, перестановок и так далее
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Исправление слова и засечение времени
def check_word(word):
    start_time = time.time()
    # list_result = spell.get_candidates(word)
    result = spell(word)
    end_time = time.time()
    print(f'Время исправления слова: {end_time - start_time} секунд\n')
    return result


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет!")


@dp.message_handler()
async def get_word(message: types.Message):
    result_word = check_word(message.text)
    if result_word == message.text:
        await message.reply('Вы правильно написали слово!')
        return
    await message.reply(f'Правильное написание Вашего слова: {result_word}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
