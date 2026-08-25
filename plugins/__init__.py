# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import os
import time
from random import choice

import requests
from telethon import Button, events
from telethon.tl import functions, types  # pylint:ignore

from pyUltroid import *
from pyUltroid._misc._assistant import asst_cmd, callback, in_pattern
from pyUltroid._misc._decorators import ultroid_cmd
from pyUltroid._misc._wrappers import eod, eor
from pyUltroid.dB import DEVLIST, ULTROID_IMAGES
from pyUltroid.fns.helper import *
from pyUltroid.fns.misc import *
from pyUltroid.fns.tools import *
from pyUltroid.startup._database import _BaseDatabase as Database
from pyUltroid.version import __version__, ultroid_version
from strings import get_help, get_string
from catbox import CatboxUploader

udB: Database

Redis = udB.get_key
con = TgConverter
quotly = Quotly()
OWNER_NAME = ultroid_bot.full_name
OWNER_ID = ultroid_bot.uid

ultroid_bot: UltroidClient
asst: UltroidClient

LOG_CHANNEL = udB.get_key("LOG_CHANNEL")


def inline_pic():
    INLINE_PIC = udB.get_key("INLINE_PIC")
    if INLINE_PIC is None:
        INLINE_PIC = choice(ULTROID_IMAGES)
    elif INLINE_PIC == False:
        INLINE_PIC = None
    return INLINE_PIC


Telegraph = telegraph_client()
cat_uploader = CatboxUploader()

upload_file = cat_uploader.upload_file

List = []
Dict = {}
InlinePlugin = {}
N = 0
cmd = ultroid_cmd
STUFF = {}

# Чаты, которые нужно игнорировать в некоторых случаях
# Их может быть много
# Не стесняйтесь добавить любой другой...

NOSPAM_CHAT = [
    -1001361294038,  # UltroidSupportChat
    -1001387666944,  # PyrogramChat
    -1001109500936,  # TelethonChat
    -1001050982793,  # Python
    -1001256902287,  # DurovsChat
    -1001473548283,  # SharingUserbot
]

KANGING_STR = [
    "Использую магию, чтобы присвоить этот стикер...",
    "Плагиаторствую, хехе...",
    "Приглашаю этот стикер в мой пак...",
    "Присваиваю этот стикер...",
    "Эй, какой классный стикер!\nНе против, если я его присвою?..",
    "Хехе, я краду твой стикер...",
    "Эй, посмотри туда (☉｡☉)!→\nПока я присваиваю этот...",
    "Розы красные, фиалки синие, присваиваю стикер, чтобы мой пак выглядел круто",
    "Заключаю этот стикер в тюрьму...",
    "Мистер-Укради-Стикер крадёт этот стикер... ",
]


ATRA_COL = [
    "DarkCyan",
    "DeepSkyBlue",
    "DarkTurquoise",
    "Cyan",
    "LightSkyBlue",
    "Turquoise",
    "MediumVioletRed",
    "Aquamarine",
    "Lightcyan",
    "Azure",
    "Moccasin",
    "PowderBlue",
]
