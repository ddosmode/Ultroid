# /usr/bin/python3
# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# Отдельный файл для локального развёртывания.

import os

a = r"""
  _    _ _ _             _     _
 | |  | | | |           (_)   | |
 | |  | | | |_ _ __ ___  _  __| |
 | |  | | | __| '__/ _ \| |/ _  |
 | |__| | | |_| | | (_) | | (_| |
  \____/|_|\__|_|  \___/|_|\__,_|
"""


def start():

    clear_screen()
    check_for_py()

    print(f"{a}\n\n")
    print("Добро пожаловать в Ultroid, давайте начнём настройку!\n\n")
    print("Клонирование репозитория...\n\n")
    os.system("rm -rf Ultroid")
    os.system("git clone https://github.com/TeamUltroid/Ultroid")
    print("\n\nГотово")
    os.chdir("Ultroid")
    clear_screen()
    print(a)
    print("\n\nДавайте начнём!\n")

    # генерировать сессию, если нужно.
    sessionisneeded = input(
        "Вы хотите сгенерировать новую сессию или у вас есть старая строка сессии? [generate/skip]",
    )
    if sessionisneeded == "generate":
        gen_session()
    elif sessionisneeded != "skip":
        print(
            'Пожалуйста, выберите "generate", чтобы сгенерировать строку сессии, или "skip", чтобы пропустить.\n\nПожалуйста, запустите скрипт снова!',
        )
        exit(0)

    # запускаем bleck megik
    print("\n\nДавайте начнём вводить переменные.\n\n")
    varrs = [
        "API_ID",
        "API_HASH",
        "SESSION",
        "REDIS_URI",
        "REDIS_PASSWORD",
    ]
    all_done = "# Ultroid Environment Variables.\n# Do not delete this file.\n\n"
    for i in varrs:
        all_done += do_input(i)
    clear_screen()
    print(a)
    print("\n\nВот то, что вы ввели.\nПожалуйста, проверьте.")
    print(all_done)
    isitdone = input("\n\nВсё правильно? [y/n]")
    if isitdone == "y" or isitdone != "n":
        # https://github.com/TeamUltroid/Ultroid/blob/31b9eb1f4f8059e0ae66adb74cb6e8174df12eac/resources/startup/locals.py#L35
        f = open(".env", "w")
        f.write(all_done)
    else:
        print("Ох, тогда давайте переделаем.")
        start()
    clear_screen()
    print("\nПоздравляем. Всё готово!\nВремя запустить бота!")
    print("\nУстановка зависимостей... Это может занять некоторое время...")
    os.system("pip3 install --no-cache-dir -r requirements.txt")
    os.system("pip3 install -r requirements.txt --break-system-packages")
    ask = input(
        "Введите 'yes/y', чтобы установить другие зависимости, необходимые для локального развёртывания."
    )
    if ask.lower().startswith("y"):
        print("Начата установка...")
        os.system(
            "pip3 install --no-cache-dir -r resources/startup/optional-requirements.txt"
        )
    else:
        print("Пропущено!")
    clear_screen()
    print(a)
    print("\nЗапуск Ultroid...")
    os.system("sh startup")


def do_input(var):
    val = input(f"Введите ваш {var}: ")
    return f"{var}={val}\n"


def clear_screen():
    # очистить экран
    _ = os.system("clear") if os.name == "posix" else os.system("cls")


def check_for_py():
    print(
        "Убедитесь, что у вас установлен python. \nПолучите его с http://python.org/\n\n",
    )
    try:
        ch = int(
            input(
                "Введите выбор:\n1. Продолжить, python установлен.\n2. Выйти и установить python.\n",
            ),
        )
    except BaseException:
        print("Пожалуйста, запустите скрипт снова и введите выбор как число!!")
        exit(0)
    if ch == 1:
        pass
    elif ch == 2:
        print("Пожалуйста, установите python и продолжайте!")
        exit(0)
    else:
        print("Вас не научили читать? Введите выбор!!")
        return


def gen_session():
    print("\nОбработка...")
    # https://github.com/TeamUltroid/Ultroid/main/resources/startup/locals.py#L35
    os.system("python3 resources/session/ssgen.py")


start()
