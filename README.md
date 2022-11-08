# Errors Corrector / Проверка орфографии
Sorry for my English. I don't know him very well and I write through a translator.

My project at Sirius College in Russian. 
The project is a telegram bot that corrects the received word, offering possible spelling options.
After the user selects the desired spelling,
the bot will write (if it finds) the rule by which the word was written.

Мой проект в Колледже "Сириус" по русскому языку.   
Проект - телеграм-бот, который исправляет полученное слово, предлагая варианты возможного написания.
После того, как пользователь выберет нужное написание, 
бот напишет (если найдёт) правило, по которому было написано слово.

## Bot link / Ссылка на бота
https://t.me/ru_corrector_bot   
(it may not work - so I turned it off)  
(может не работать - значит я его выключил)


## Warning / Предупреждение
In Russian:
1) Add the bot token to the BOT_TOKEN variable in config.py or directly to main.py
2) The bot only works with Russian. But to make it work, move 2 files from the localize folder
to the library folder:
- If you don't use venv, folder: C:\...\Python\Python36\site-packages\enchant\data\mingw64\share\enchant\hunspell
- If you use venv, folder: ...\venv\Lib\site-packages\enchant\data\mingw64\share\enchant\hunspell


На русском:
1) Добавьте токен бота в переменную BOT_TOKEN в config.py или напрямую в main.py
2) Бот работает только с русским языком. Но чтобы он работал - переместите 2 файла из папки localize
в папку с библиотекой:
- Если Вы не используете venv, папка: C:\...\Python\Python36\site-packages\enchant\data\mingw64\share\enchant\hunspell
- Если Вы используете venv, папка: ...\venv\Lib\site-packages\enchant\data\mingw64\share\enchant\hunspell

## Another language / Другой язык
