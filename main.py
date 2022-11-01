from autocorrect import Speller
spell = Speller('ru')


def check_word(word):
    import time

    start_time = time.time()
    print(spell(word))
    end_time = time.time()
    print(f'Время выполнения программы: {end_time - start_time} \n')


def corrector():
    while True:
        input_word = input('Введите слово (чтобы выйти введите "выход"): ')
        if input_word == 'выход':
            return
        check_word(input_word)


if __name__ == '__main__':
    corrector()
