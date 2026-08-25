#!/usr/bin/python3
# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
from time import sleep

ULTROID = r"""
  _    _ _ _             _     _
 | |  | | | |           (_)   | |
 | |  | | | |_ _ __ ___  _  __| |
 | |  | | | __| '__/ _ \| |/ _  |
 | |__| | | |_| | | (_) | | (_| |
  \____/|_|\__|_|  \___/|_|\__,_|
"""


def spinner(x):
    if x == "tele":
        print("Проверка установки Telethon...")
    else:
        print("Проверка установки Pyrogram...")
    for _ in range(3):
        for frame in r"-\|/-\|/":
            print("\b", frame, sep="", end="", flush=True)
            sleep(0.1)


def clear_screen():
    # Очистка экрана. См. https://www.tutorialspoint.com/how-to-clear-screen-in-python#:~:text=In%20Python%20sometimes%20we%20have,screen%20by%20pressing%20Control%20%2B%20l%20.
    if os.name == "posix":
        os.system("clear")
    else:
        # для платформы Windows
        os.system("cls")


def get_api_id_and_hash():
    print(
        "Получите API ID и API HASH с my.telegram.org или от @ScrapperRoBot для продолжения.\n\n",
    )
    try:
        API_ID = int(input("Пожалуйста, введите ваш API ID: "))
    except ValueError:
        print("APP ID должен быть целым числом.\nВыход...")
        exit(0)
    API_HASH = input("Пожалуйста, введите ваш API HASH: ")
    return API_ID, API_HASH


def telethon_session():
    try:
        spinner("tele")
        import telethon
        x = "\bНайдена существующая установка Telethon...\nУспешно импортировано.\n\n"
    except ImportError:
        print("Установка Telethon...")
        os.system("pip uninstall telethon -y && pip install -U telethon")

        x = "\bГотово. Telethon установлен и импортирован."
    clear_screen()
    print(ULTROID)
    print(x)

    # импорты

    from telethon.errors.rpcerrorlist import (
        ApiIdInvalidError,
        PhoneNumberInvalidError,
        UserIsBotError,
    )
    from telethon.sessions import StringSession
    from telethon.sync import TelegramClient

    API_ID, API_HASH = get_api_id_and_hash()

    # вход в систему
    try:
        with TelegramClient(StringSession(), API_ID, API_HASH) as ultroid:
            print("Генерация строковой сессии для •ULTROID•")
            try:
                ultroid.send_message(
                    "me",
                    f"**ULTROID** `SESSION`:\n\n`{ultroid.session.save()}`\n\n**Никому не показывайте это!**",
                )
                print(
                    "Ваша SESSION была сгенерирована. Проверьте сохранённые сообщения в Telegram!"
                )
                return
            except UserIsBotError:
                print("Вы пытаетесь сгенерировать сессию для аккаунта вашего бота?")
                print("Вот она!\n{ultroid.session.save()}\n\n")
                print("ПРИМЕЧАНИЕ: Вы не можете использовать это как пользовательскую сессию..")
    except ApiIdInvalidError:
        print(
            "Ваша комбинация API ID/API HASH неверна. Пожалуйста, проверьте.\nВыход..."
        )
        exit(0)
    except ValueError:
        print("API HASH не должен быть пустым!\nВыход...")
        exit(0)
    except PhoneNumberInvalidError:
        print("Номер телефона неверен!\nВыход...")
        exit(0)
    except Exception as er:
        print("Произошла непредвиденная ошибка при создании сессии")
        print(er)
        print("Если вы считаете это ошибкой, сообщите в @UltroidSupportChat.\n\n")


def pyro_session():
    try:
        spinner("pyro")
        from pyrogram import Client

        x = "\bНайдена существующая установка Pyrogram...\nУспешно импортировано.\n\n"
    except BaseException:
        print("Установка Pyrogram...")
        os.system("pip install pyrogram tgcrypto")
        x = "\bГотово. Pyrogram установлен и импортирован."
        from pyrogram import Client
        
    clear_screen()
    print(ULTROID)
    print(x)

    # генерировать сессию
    API_ID, API_HASH = get_api_id_and_hash()
    print("Введите номер телефона, когда спросят.\n\n")
    try:
        with Client(name="ultroid", api_id=API_ID, api_hash=API_HASH, in_memory=True) as pyro:
            ss = pyro.export_session_string()
            pyro.send_message(
                "me",
                f"`{ss}`\n\nВыше ваша строка сессии Pyrogram для @TheUltroid. **НЕ ПОКАЗЫВАЙТЕ ЕЁ.**",
            )
            print("Сессия была отправлена в ваши сохранённые сообщения!")
            exit(0)
    except Exception as er:
      print("Произошла непредвиденная ошибка при создании сессии, убедитесь, что вы правильно ввели данные.")
      print(er)


def main():
    clear_screen()
    print(ULTROID)
    try:
        type_of_ss = int(
            input(
                "\nUltroid поддерживает как сессии Telethon, так и Pyrogram.\n\nКакую сессию вы хотите сгенерировать?\n1. Сессия Telethon.\n2. Сессия Pyrogram.\n\nВведите выбор:  "
            )
        )
    except Exception as e:
        print(e)
        exit(0)
    if type_of_ss == 1:
        telethon_session()
    elif type_of_ss == 2:
        pyro_session()
    else:
        print("Неверный выбор.")
    x = input("Запустить снова? (Y/n)")
    if x.lower() in ["y", "yes"]:
        main()
    else:
        exit(0)


main()
