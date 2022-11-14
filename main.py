import asyncio
import app_logger
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.word import register_handlers_word


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Старт")
    ]
    await bot.set_my_commands(commands)


async def main():
    logger = app_logger.get_logger(__name__)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # регистрация хэндлеров
    register_handlers_word(dp)

    # установка команд
    await set_commands(bot)

    # запуск бота
    logger.warning('Bot is running')
    # TODO: возможно запилить поддержку предложений (и словосочетаний с значением, например пре-, при-)
    # TODO: сделать красивое оформление
    await dp.start_polling(bot)
    logger.warning('Bot is stopped')
    # TODO: при отключении бота выдаёт Runtime ошибку


if __name__ == '__main__':
    asyncio.run(main())
