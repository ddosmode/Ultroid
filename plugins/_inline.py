# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
import time
from datetime import datetime
from os import remove

from git import Repo
from telethon import Button
from telethon.tl.types import InputWebDocument, Message
from telethon.utils import resolve_bot_file_id

from pyUltroid._misc._assistant import callback, in_pattern
from pyUltroid.dB._core import HELP, LIST
from pyUltroid.fns.helper import gen_chlog, time_formatter, updater
from pyUltroid.fns.misc import split_list

from . import (
    HNDLR,
    LOGS,
    OWNER_NAME,
    InlinePlugin,
    asst,
    get_string,
    inline_pic,
    split_list,
    start_time,
    udB,
)
from ._help import _main_help_menu

# ================================================#

helps = get_string("inline_1")

add_ons = udB.get_key("ADDONS")

zhelps = get_string("inline_3") if add_ons is False else get_string("inline_2")
PLUGINS = HELP.get("Official", [])
ADDONS = HELP.get("Addons", [])
upage = 0
# ============================================#

# --------------------КНОПКИ--------------------#

SUP_BUTTONS = [
    [
        Button.url("• Репозиторий •", url="https://github.com/TeamUltroid/Ultroid"),
        Button.url("• Поддержка •", url="t.me/UltroidSupportChat"),
    ],
]

# --------------------КНОПКИ--------------------#


@in_pattern(owner=True, func=lambda x: not x.text)
async def inline_alive(o):
    TLINK = inline_pic() or "https://graph.org/file/74d6259983e0642923fdb.jpg"
    MSG = "• **Ultroid Userbot •**"
    WEB0 = InputWebDocument(
        "https://graph.org/file/acd4f5d61369f74c5e7a7.jpg", 0, "image/jpg", []
    )
    RES = [
        await o.builder.article(
            type="photo",
            text=MSG,
            include_media=True,
            buttons=SUP_BUTTONS,
            title="Ultroid Userbot",
            description="Юзербот | Telethon",
            url=TLINK,
            thumb=WEB0,
            content=InputWebDocument(TLINK, 0, "image/jpg", []),
        )
    ]
    await o.answer(
        RES,
        private=True,
        cache_time=300,
        switch_pm="👥 ПОРТАЛ ULTROID",
        switch_pm_param="start",
    )


@in_pattern("ultd", owner=True)
async def inline_handler(event):
    z = []
    for x in LIST.values():
        z.extend(x)
    text = get_string("inline_4").format(
        OWNER_NAME,
        len(HELP.get("Official", [])),
        len(HELP.get("Addons", [])),
        len(z),
    )
    if inline_pic():
        result = await event.builder.photo(
            file=inline_pic(),
            link_preview=False,
            text=text,
            buttons=_main_help_menu,
        )
    else:
        result = await event.builder.article(
            title="Меню помощи Ultroid", text=text, buttons=_main_help_menu
        )
    await event.answer([result], private=True, cache_time=300, gallery=True)


@in_pattern("pasta", owner=True)
async def _(event):
    ok = event.text.split("-")[1]
    if not ok.startswith("http"):
        link = f"https://spaceb.in/{ok}"
        raw = f"https://spaceb.in/api/v1/documents/{ok}/raw"
    else:
        link = ok
        raw = f"{ok}/raw"
    result = await event.builder.article(
        title="Вставка",
        text="Вставлено в Spacebin 🌌",
        buttons=[
            [
                Button.url("SpaceBin", url=link),
                Button.url("Исходник", url=raw),
            ],
        ],
    )
    await event.answer([result])


@callback("ownr", owner=True)
async def setting(event):
    z = []
    for x in LIST.values():
        z.extend(x)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(HELP.get("Official", [])),
            len(HELP.get("Addons", [])),
            len(z),
        ),
        file=inline_pic(),
        link_preview=False,
        buttons=[
            [
                Button.inline("•Пинг•", data="pkng"),
                Button.inline("•Аптайм•", data="upp"),
            ],
            [
                Button.inline("•Статистика•", data="alive"),
                Button.inline("•Обновление•", data="doupdate"),
            ],
            [Button.inline("« Назад", data="open")],
        ],
    )


_strings = {"Official": helps, "Addons": zhelps, "VCBot": get_string("inline_6")}


@callback(re.compile("uh_(.*)"), owner=True)
async def help_func(ult):
    key, count = ult.data_match.group(1).decode("utf-8").split("_")
    if key == "VCBot" and HELP.get("VCBot") is None:
        return await ult.answer(get_string("help_12"), alert=True)
    elif key == "Addons" and HELP.get("Addons") is None:
        return await ult.answer(get_string("help_13").format(HNDLR), alert=True)
    if "|" in count:
        _, count = count.split("|")
    count = int(count) if count else 0
    text = _strings.get(key, "").format(OWNER_NAME, len(HELP.get(key)))
    await ult.edit(text, buttons=page_num(count, key), link_preview=False)
