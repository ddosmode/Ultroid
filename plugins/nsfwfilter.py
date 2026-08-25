# Ultroid - ЮзерБот
# Авторские права (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License в
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

•`{i}addnsfw <ban/mute/kick>`
   Если кто-то отправляет контент 18+, он будет удалён, и будет принято соответствующее действие.

•`{i}remnsfw`
    Удалить чат из NSFW-фильтрации.
"""

import os

from . import LOGS

try:
    from ProfanityDetector import detector
except ImportError:
    detector = None
    LOGS.error("nsfwfilter: 'Profanitydetector' не установлен!")
from pyUltroid.dB.nsfw_db import is_nsfw, nsfw_chat, rem_nsfw

from . import HNDLR, async_searcher, eor, events, udB, ultroid_bot, ultroid_cmd


@ultroid_cmd(pattern="addnsfw( (.*)|$)", admins_only=True)
async def addnsfw(e):
    if not udB.get_key("DEEP_API"):
        return await eor(
            e, f"Получите API с deepai.org и добавьте его `{HNDLR}setdb DEEP_API your-api`"
        )
    action = e.pattern_match.group(1).strip()
    if not action or ("ban" or "kick" or "mute") not in action:
        action = "mute"
    nsfw_chat(e.chat_id, action)
    ultroid_bot.add_handler(nsfw_check, events.NewMessage(incoming=True))
    await e.eor("Чат добавлен в NSFW-фильтр")


@ultroid_cmd(pattern="remnsfw", admins_only=True)
async def remnsfw(e):
    rem_nsfw(e.chat_id)
    await e.eor("Чат удалён из NSFW-фильтра.")


NWARN = {}


async def nsfw_check(e):
    chat = e.chat_id
    action = is_nsfw(chat)
    if action and udB.get_key("DEEP_API") and e.media:
        pic, name, nsfw = "", "", 0
        try:
            pic = await e.download_media(thumb=-1)
        except BaseException:
            pass
        if e.file:
            name = e.file.name
        if detector and name:
            x, y = detector(name)
            if y:
                nsfw += 1
        if pic and not nsfw:
            r = await async_searcher(
                "https://api.deepai.org/api/nsfw-detector",
                data={
                    "image": open(pic, "rb"),
                },
                post=True,
                re_json=True,
                headers={"api-key": udB.get_key("DEEP_API")},
            )
            try:
                k = float((r["output"]["nsfw_score"]))
            except KeyError as er:
                LOGS.exception(er)
                LOGS.info(r)
                return
            score = int(k * 100)
            if score > 45:
                nsfw += 1
            os.remove(pic)
        if nsfw:
            await e.delete()
            if NWARN.get(e.sender_id):
                count = NWARN[e.sender_id] + 1
                if count < 3:
                    NWARN.update({e.sender_id: count})
                    return await ultroid_bot.send_message(
                        chat,
                        f"**NSFW предупреждение {count}/3** Для [{e.sender.first_name}](tg://user?id={e.sender_id})\nNSFW запрещён! Повторное нарушение приведёт к {action}",
                    )
                if "mute" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            chat, e.sender_id, until_date=None, send_messages=False
                        )
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Действие выполнено** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nНевозможно {action}.",
                        )
                elif "ban" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            chat, e.sender_id, view_messages=False
                        )
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Действие выполнено** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nНевозможно {action}.",
                        )
                elif "kick" in action:
                    try:
                        await ultroid_bot.kick_participant(chat, e.sender_id)
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\n**Действие выполнено** : {action}",
                        )
                    except BaseException:
                        await ultroid_bot.send_message(
                            chat,
                            f"NSFW предупреждение 3/3 для [{e.sender.first_name}](tg://user?id={e.sender_id})\n\nНевозможно {action}.",
                        )
                NWARN.pop(e.sender_id)
            else:
                NWARN.update({e.sender_id: 1})
                return await ultroid_bot.send_message(
                    chat,
                    f"**NSFW предупреждение 1/3** Для [{e.sender.first_name}](tg://user?id={e.sender_id})\nNSFW запрещён! Повторное нарушение приведёт к {action}",
                )


if udB.get_key("NSFW"):
    ultroid_bot.add_handler(nsfw_check, events.NewMessage(incoming=True))
