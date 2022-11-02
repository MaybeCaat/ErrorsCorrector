import asyncio
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
    import time

    start_time = time.time()
    print(spell.get_candidates(word))
    print(spell(word))
    end_time = time.time()
    print(f'Время выполнения программы: {end_time - start_time} \n')


def corrector():
    while True:
        input_word = input('Введите слово (чтобы выйти введите "выход"): ')
        # Стоп-слово для выхода из программы
        if input_word == 'выход':
            return
        check_word(input_word)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    # corrector()
