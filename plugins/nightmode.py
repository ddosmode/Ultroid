# Ultroid - UserBot
# Авторские права (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

Ночью он отключает всем разрешение на отправку сообщений во всех группах, которые вы добавили через `{i}addnight`
И автоматически включает утром

• `{i}addnm`
   Добавить Ночной режим
   Чтобы добавить группу в Авто Ночной режим.

• `{i}remnm`
   Удалить Ночной режим
   Чтобы удалить группу из Авто Ночного режима

• `{i}listnm`
   Список Ночного режима
   Чтобы получить полный список групп, где активен Ночной режим.

• `{i}nmtime <час закрытия> <минута закрытия> <час открытия> <минута открытия>`
   Время Ночного режима
   По умолчанию закрытие в 00:00 , открытие в 07:00
   Используйте 24-часовой формат
   Например- `nmtime 01 00 06 30`
"""

from . import LOGS

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError:
    LOGS.error("nightmode: 'apscheduler' не установлен!")
    AsyncIOScheduler = None

from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

from pyUltroid.dB.base import KeyManager

from . import get_string, udB, ultroid_bot, ultroid_cmd

keym = KeyManager("NIGHT_CHATS", cast=list)


@ultroid_cmd(pattern="nmtime( (.*)|$)")
async def set_time(e):
    if not e.pattern_match.group(1).strip():
        return await e.eor(get_string("nightm_1"))
    try:
        ok = e.text.split(maxsplit=1)[1].split()
        if len(ok) != 4:
            return await e.eor(get_string("nightm_1"))
        tm = [int(x) for x in ok]
        udB.set_key("NIGHT_TIME", str(tm))
        await e.eor(get_string("nightm_2"))
    except BaseException:
        await e.eor(get_string("nightm_1"))


@ultroid_cmd(pattern="addnm( (.*)|$)")
async def add_grp(e):
    if pat := e.pattern_match.group(1).strip():
        try:
            keym.add((await ultroid_bot.get_entity(pat)).id)
            return await e.eor(f"Готово, добавлено {pat} в Ночной режим.")
        except BaseException:
            return await e.eor(get_string("nightm_5"), time=5)
    keym.add(e.chat_id)
    await e.eor(get_string("nightm_3"))


@ultroid_cmd(pattern="remnm( (.*)|$)")
async def r_em_grp(e):
    if pat := e.pattern_match.group(1).strip():
        try:
            keym.remove((await ultroid_bot.get_entity(pat)).id)
            return await e.eor(f"Готово, удалено {pat} из Ночного режима.")
        except BaseException:
            return await e.eor(get_string("nightm_5"), time=5)
    keym.remove(e.chat_id)
    await e.eor(get_string("nightm_4"))


@ultroid_cmd(pattern="listnm$")
async def rem_grp(e):
    chats = keym.get()
    name = "Группы с Ночным режимом:-:\n\n"
    for x in chats:
        try:
            ok = await ultroid_bot.get_entity(x)
            name += f"@{ok.username}" if ok.username else ok.title
        except BaseException:
            name += str(x)
    await e.eor(name)


async def open_grp():
    for chat in keym.get():
        try:
            await ultroid_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=False,
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        send_polls=False,
                    ),
                )
            )
            await ultroid_bot.send_message(chat, "**Ночной режим выключен**\n\nГруппа открыта 🥳.")
        except Exception as er:
            LOGS.info(er)


async def close_grp():
    __, _, h2, m2 = 0, 0, 7, 0
    if udB.get_key("NIGHT_TIME"):
        _, __, h2, m2 = eval(udB.get_key("NIGHT_TIME"))
    for chat in keym.get():
        try:
            await ultroid_bot(
                EditChatDefaultBannedRightsRequest(
                    chat,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        send_messages=True,
                    ),
                )
            )
            await ultroid_bot.send_message(
                chat, f"**Ночной режим : Группа закрыта**\n\nГруппа откроется в `{h2}:{m2}`"
            )
        except Exception as er:
            LOGS.info(er)


if AsyncIOScheduler and keym.get():
    try:
        h1, m1, h2, m2 = 0, 0, 7, 0
        if udB.get_key("NIGHT_TIME"):
            h1, m1, h2, m2 = eval(udB.get_key("NIGHT_TIME"))
        sch = AsyncIOScheduler()
        sch.add_job(close_grp, trigger="cron", hour=h1, minute=m1)
        sch.add_job(open_grp, trigger="cron", hour=h2, minute=m2)
        sch.start()
    except Exception as er:
        LOGS.info(er)
