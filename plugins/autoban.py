# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_autoban")

from telethon import events

from pyUltroid.dB.base import KeyManager

from . import LOGS, asst, ultroid_bot, ultroid_cmd

Keym = KeyManager("DND_CHATS", cast=list)


def join_func(e):
    return e.user_joined and Keym.contains(e.chat_id)


async def dnd_func(event):
    for user in event.users:
        try:
            await (await event.client.kick_participant(event.chat_id, user)).delete()
        except Exception as ex:
            LOGS.error("Ошибка в DND:")
            LOGS.exception(ex)
    await event.delete()


@ultroid_cmd(
    pattern="autokick (on|off)$",
    admins_only=True,
    manager=True,
    require="ban_users",
    fullsudo=True,
)
async def _(event):
    match = event.pattern_match.group(1)
    if match == "on":
        if Keym.contains(event.chat_id):
            return await event.eor("`Чат уже в режиме не беспокоить.`", time=3)
        Keym.add(event.chat_id)
        event.client.add_handler(dnd_func, events.ChatAction(func=join_func))
        await event.eor("`Режим не беспокоить активирован для этого чата.`", time=3)
    elif match == "off":
        if not Keym.contains(event.chat_id):
            return await event.eor("`Чат не в режиме не беспокоить.`", time=3)
        Keym.remove(event.chat_id)
        await event.eor("`Режим не беспокоить деактивирован для этого чата.`", time=3)


if Keym.get():
    ultroid_bot.add_handler(dnd_func, events.ChatAction(func=join_func))
    asst.add_handler(dnd_func, events.ChatAction(func=join_func))
