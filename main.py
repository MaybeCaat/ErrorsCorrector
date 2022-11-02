from autocorrect import Speller
spell = Speller('ru', only_replacements=True)
# only_replacements - только замены букв в слове, нет пропуска букв, перестановок и так далее


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


if __name__ == '__main__':
    corrector()
