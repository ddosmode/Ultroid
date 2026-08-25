# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon import events

from . import *


@asst.on(events.ChatAction(func=lambda x: x.user_added))
async def dueha(e):
    user = await e.get_user()
    if not user.is_self:
        return
    sm = udB.get_key("ON_MNGR_ADD")
    if sm == "OFF":
        return
    if not sm:
        sm = "Спасибо, что добавили меня :)"
    await e.reply(sm, link_preview=False)