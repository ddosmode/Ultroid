# TeleFriend - Пользовательский бот
# Авторские права (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_afk")


import asyncio

from telethon import events

from pyUltroid.dB.afk_db import add_afk, del_afk, is_afk
from pyUltroid.dB.base import KeyManager

from . import (
    LOG_CHANNEL,
    NOSPAM_CHAT,
    Redis,
    asst,
    get_string,
    mediainfo,
    udB,
    ultroid_bot,
    ultroid_cmd,
    upload_file
)

old_afk_msg = []

is_approved = KeyManager("PMPERMIT", cast=list).contains


@ultroid_cmd(pattern="afk( (.*)|$)", owner_only=True)
async def set_afk(event):
    if event.client._bot or is_afk():
        return
    text, media, media_type = None, None, None
    if event.pattern_match.group(1).strip():
        text = event.text.split(maxsplit=1)[1]
    reply = await event.get_reply_message()
    if reply:
        if reply.text and not text:
            text = reply.text
        if reply.media:
            media_type = mediainfo(reply.media)
            if media_type.startswith(("pic", "gif")):
                file = await event.client.download_media(reply.media)
                media = upload_file(file)
            else:
                media = reply.file.id
    await event.eor("`Готово`", time=2)
    add_afk(text, media_type, media)
    ultroid_bot.add_handler(remove_afk, events.NewMessage(outgoing=True))
    ultroid_bot.add_handler(
        on_afk,
