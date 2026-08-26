# TeleFriend - Юзербот
# Copyright (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License по адресу
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.
"""
✘ Доступные команды -

•`{i}addprofanity`
   Если кто-то отправит нецензурное слово в чат, бот удалит это сообщение.

•`{i}remprofanity`
   Убрать чат из списка нецензурных слов.

"""

from pyUltroid.dB.nsfw_db import profan_chat, rem_profan

from . import get_string, ultroid_cmd


@ultroid_cmd(pattern="(add|rem)profanity$", admins_only=True)
async def addp(e):
    cas = e.pattern_match.group(1)
    add = cas == "add"
    if add:
        profan_chat(e.chat_id, "mute")
        await e.eor(get_string("prof_1"), time=10)
        return
    rem_profan(e.chat_id)
    await e.eor(get_string("prof_2"), time=10)
