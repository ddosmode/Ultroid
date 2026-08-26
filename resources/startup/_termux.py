# /usr/bin/python3
from datetime import datetime
from os import path, system
from time import sleep

from colorama import Back, Fore, Style


# очистить экран
def clear():
    system("clear")


MANDATORY_REQS = [
    "https://github.com/New-dev0/Telethon/archive/Cartoon.zip",
    "gitpython",
    "enhancer",
    "telegraph",
    "requests",
    "python-decouple",
    "aiohttp",
]

OPT_PACKAGES = {
    "bs4": "Используется для парсинга сайтов (используется в командах, таких как .gadget и многих других)",
    "yt-dlp": "Используется для загрузок, связанных с YouTube...",
    "youtube-search-python": "Используется для поиска видео на YouTube..",
    "pillow": "Используется для задач, связанных с конвертацией изображений. (размер - около 50 МБ) (требуется для kang, convert и многих других.)",
    "psutil": "Используется для команды .usage.",
    "lottie": "Используется для конвертации анимированных стикеров.",
    "apscheduler": "Используется в autopic/nightmode (планирование задач.)",
    # "git+https://github.com/1danish-00/google_trans_new.git": "Используется для целей перевода.",
}

APT_PACKAGES = ["ffmpeg", "neofetch", "mediainfo"]

DISCLAIMER_TEXT = ""

COPYRIGHT = f"©️ TeamTeleFriend {datetime.now().year}"

HEADER = f"""{Fore.MAGENTA}
╔╗ ╔╗╔╗  ╔╗            ╔╗
║║ ║║║║ ╔╝╚╗           ║║
║║ ║║║║ ╚╗╔╝╔═╗╔══╗╔╗╔═╝║
║║ ║║║║  ║║ ║╔╝║╔╗║╠╣║╔╗║
║╚═╝║║╚╗ ║╚╗║║ ║╚╝║║║║╚╝║
╚═══╝╚═╝ ╚═╝╚╝ ╚══╝╚╝╚══╝\n{Fore.RESET}
"""

INFO_TEXT = f"""
{Fore.GREEN}# Важные моменты, которые нужно знать.

{Fore.YELLOW}1. Этот скрипт установит только базовые зависимости, из-за чего некоторые команды, у которых отсутствуют зависимости, не будут работать. Вы можете просмотреть все дополнительные зависимости в (./resources/startup/optional-requirements.txt)

2. Вы можете установить эту зависимость в любое время с помощью 'pip install' (требуются очень базовые знания python+bash.)

3. Некоторые плагины отключены для 'Пользователей Termux' для экономии ресурсов (путем добавления в EXCLUDE_OFFICIAL).
   - Подробнее - https://t.me/TeleFriendUpdates/36
   - Также способ включить отключенные плагины указан в этом посте.

   # Имена отключенных плагинов
     -    autocorrect    -     compressor
     -    Gdrive         -     instagram
     -    nsfwfilter     -     glitch
     -    pdftools       -     writer
     -    youtube        -     megadl
     -    autopic        -     nightmode
     -    blacklist      -     forcesubscribe

4. Вы не можете использовать 'VCBOT' в Termux.

5. Вы не можете использовать 'MongoDB' в Termux (Android).
{Fore.RESET}
* Надеюсь, вы достаточно умны, чтобы понять.
* Введите 'A' для продолжения, 'E' для выхода..\n
"""


def ask_and_wait(text, header: bool = False):
    if header:
        text = with_header(text)
    print(text + "\nНажмите 'ЛЮБУЮ клавишу' для продолжения или 'Ctrl+C' для выхода...\n")
    input("")


def with_header(text):
    return HEADER + "\n\n" + text


def yes_no_apt():
    yes_no = input("").strip().lower()
    if yes_no in ["yes", "y"]:
        return True
    elif yes_no in ["no", "n"]:
        return False
    print("Неверный ввод\nПовторите ввод: ")
    return yes_no_apt()


def ask_process_info_text():
    strm = input("").lower().strip()
    if strm == "e":
        print("Выход...")
        exit(0)
    elif strm != "a":
        print("Неверный ввод")
        print("Введите 'A' для продолжения или 'E' для выхода...")
        ask_process_info_text()


def ask_process_apt_install():
    strm = input("").lower().strip()
    if strm == "e":
        print("Выход...")
        exit(0)
    elif strm == "a":
        for apt in APT_PACKAGES:
            print(f"* Do you want to install '{apt}'? [Y/N] ")
            if yes_no_apt():
                print(f"Установка {apt}...")
                system(f"apt install {apt} -y")
            else:
                print(f"- Отменено {apt}.\n")
    elif strm == "i":
        names = " ".join(APT_PACKAGES)
        print("Установка всех apt-пакетов...")
        system(f"apt install {names} -y")
    elif strm != "s":
        print("Неверный ввод\n* Введите снова...")
        ask_process_apt_install()


def ask_and_wait_opt():
    strm = input("").strip().lower()
    if strm == "e":
        print("Выход...")
        exit(0)
    elif strm == "a":
        for opt in OPT_PACKAGES.keys():
            print(
                f"* {Fore.YELLOW}Вы хотите установить '{opt}'? [Y/N]\n- {OPT_PACKAGES[opt]}"
            )
            if yes_no_apt():
                print(f"Установка {opt}...")
                system(f"pip install {opt}")
            else:
                print(f"{Fore.YELLOW}- Отменено {opt}.\n")
    elif strm == "i":
        names = " ".join(OPT_PACKAGES.keys())
        print(f"{Fore.YELLOW}Установка всех пакетов...")
        system(f"pip install {names}")
    elif strm != "s":
        print("Неверный ввод\n* Введите снова...")
        ask_and_wait_opt()


def ask_make_env():
    strm = input("").strip().lower()
    if strm in ["yes", "y"]:
        print(f"{Fore.YELLOW}* Создание файла .env..")
        with open(".env", "a") as file:
            for var in ["API_ID", "API_HASH", "SESSION", "REDIS_URI", "REDIS_PASSWORD"]:
                inp = input(f"Введите {var}\n- ")
                file.write(f"{var}={inp}\n")
        print("* Файл '.env' успешно создан! 😃")

    else:
        print("OK!")


# ------------------------------------------------------------------------------------------ #

clear()

print(
    f"""
{Fore.BLACK}{Back.WHITE} _____________ 
 ▄▄   ▄▄ ▄▄▄     ▄▄▄▄▄▄▄ ▄▄▄▄▄▄   ▄▄▄▄▄▄▄ ▄▄▄ ▄▄▄▄▄▄  
█  █ █  █   █   █       █   ▄  █ █       █   █      █ 
█  █ █  █   █   █▄     ▄█  █ █ █ █   ▄   █   █  ▄    █
█  █▄█  █   █     █   █ █   █▄▄█▄█  █ █  █   █ █ █   █
█       █   █▄▄▄  █   █ █    ▄▄  █  █▄█  █   █ █▄█   █
█       █       █ █   █ █   █  █ █       █   █       █
█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█ █▄▄▄█ █▄▄▄█  █▄█▄▄▄▄▄▄▄█▄▄▄█▄▄▄▄▄▄█ 
{Style.RESET_ALL}
{Fore.GREEN}- Установка ULTROID в Termux -
  Основная цель этого скрипта - развернуть TeleFriend с базовыми зависимостями и сэкономить ресурсы вашего телефона.
{Fore.RESET}

{COPYRIGHT}
    """
)
print("Нажмите 'Любую клавишу' для продолжения...")
input("")
clear()

print(with_header(INFO_TEXT))
ask_process_info_text()

clear()

print(with_header("Установка обязательных зависимостей..."))
all_ = " ".join(MANDATORY_REQS)
system(f"pip install {all_}")

clear()
print(
    with_header(
        f"\n{Fore.GREEN}# Переход к установке Apt-пакетов{Fore.RESET}\n\n"
    )
)
print("---Ввод---")
print(" - A = 'Спрашивать Y/N для каждого'.")
print(" - I = 'Установить все'")
print(" - S = 'Пропустить установку Apt.'")
print(" - E = Выход.\n")
ask_process_apt_install()

clear()
print(
    with_header(
        f"""
{Fore.YELLOW}# Установка других необязательных зависимостей.
(Вы можете установить их, если хотите, чтобы команды, использующие их, работали!){Fore.RESET}

{' - '.join(list(OPT_PACKAGES.keys()))}

Введите [ A = Спросить для каждого, I = Установить все, S = Пропустить, E = Выход]"""
    )
)
ask_and_wait_opt()

print(f"\n{Fore.RED}#ДОПОЛНИТЕЛЬНЫЕ возможности...\n")
print(f"{Fore.YELLOW}* Вы хотите получать логи TeleFriend в цветах? [Y/N] ")
inp = input("").strip().lower()
if inp in ["yes", "y"]:
    print(f"{Fore.GREEN}*Произносим волшебные мантры*")
    system("pip install coloredlogs")
else:
    print("Пропущено!")

clear()
if not path.exists(".env"):
    print(with_header("# Вы хотите перейти к созданию файла .env ? [y/N] "))
    ask_make_env()

print(with_header(f"\n{Fore.GREEN}Вы всё сделали! 🥳"))
sleep(0.2)
print(f"Используйте 'bash startup', чтобы попробовать запустить TeleFriend.{Fore.RESET}")
sleep(0.5)
print(
    "\nВы можете обратиться к @TeleFriendSupportChat, если застряли где-то и нуждаетесь в помощи."
)
sleep(0.5)
print("\nСделано с ❤️ от @TeamTeleFriend...")

system("pip3 uninstall -q colorama -y")
