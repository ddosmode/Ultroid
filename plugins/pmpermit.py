"""
✘ Доступные команды -

• `{i}a` или `{i}approve`
    Одобрить пользователя для личных сообщений.

• `{i}da` или `{i}disapprove`
    Отозвать одобрение пользователя для личных сообщений.

• `{i}block`
    Заблокировать пользователя.

• `{i}unblock` | `{i}unblock all`
    Разблокировать пользователя.

• `{i}nologpm`
    Прекратить логирование сообщений от пользователя.

• `{i}logpm`
    Начать логирование сообщений от пользователя.

• `{i}startarchive`
    Архивировать новые личные сообщения.

• `{i}stoparchive`
    Не архивировать новые личные сообщения.

• `{i}cleararchive`
    Разархивировать все чаты.

• `{i}listapproved`
   Показать всех одобренных пользователей ЛС.
"""

import asyncio
import re
from os import remove

from pyUltroid.dB import DEVLIST

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None
from telethon import events
from telethon.errors import MessageNotModifiedError
from telethon.tl.functions.contacts import (
    BlockRequest,
    GetBlockedRequest,
    UnblockRequest,
)
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.utils import get_display_name, resolve_bot_file_id

from pyUltroid.dB.base import KeyManager

from . import *

# ========================= CONSTANTS =============================

COUNT_PM = {}
LASTMSG = {}
WARN_MSGS = {}
U_WARNS = {}
if isinstance(udB.get_key("PMPERMIT"), (int, str)):
    value = [udB.get_key("PMPERMIT")]
    udB.set_key("PMPERMIT", value)
keym = KeyManager("PMPERMIT", cast=list)
Logm = KeyManager("LOGUSERS", cast=list)
PMPIC = udB.get_key("PMPIC")
LOG_CHANNEL = udB.get_key("LOG_CHANNEL")
UND = get_string("pmperm_1")
UNS = get_string("pmperm_2")
NO_REPLY = get_string("pmperm_3")

UNAPPROVED_MSG = "**Безопасность ЛС от {ON}!**\n\n{UND}\n\nУ вас {warn}/{twarn} предупреждений!"
if udB.get_key("PM_TEXT"):
    UNAPPROVED_MSG = (
        "**Безопасность ЛС от {ON}!**\n\n"
        + udB.get_key("PM_TEXT")
        + "\n\nУ вас {warn}/{twarn} предупреждений!"
    )
# 1
WARNS = udB.get_key("PMWARNS") or 4
PMCMDS = [
    f"{HNDLR}a",
    f"{HNDLR}approve",
    f"{HNDLR}da",
    f"{HNDLR}disapprove",
    f"{HNDLR}block",
    f"{HNDLR}unblock",
]

_not_approved = {}
_to_delete = {}

my_bot = asst.me.username


def update_pm(userid, message, warns_given):
    try:
        WARN_MSGS.update({userid: message})
    except KeyError:
        pass
    try:
        U_WARNS.update({userid: warns_given})
    except KeyError:
        pass


async def delete_pm_warn_msgs(chat: int):
    try:
        await _to_delete[chat].delete()
    except KeyError:
        pass


# =================================================================


if udB.get_key("PMLOG"):

    @ultroid_cmd(
        pattern="logpm$",
    )
    async def _(e):
        if not e.is_private:
            return await e.eor("`Используйте меня в личных сообщениях.`", time=3)
        if not Logm.contains(e.chat_id):
            return await e.eor("`Здесь не велось логирование сообщений.`", time=3)

        Logm.remove(e.chat_id)
        return await e.eor("`Теперь я буду логировать сообщения отсюда.`", time=3)

    @ultroid_cmd(
        pattern="nologpm$",
    )
    async def _(e):
        if not e.is_private:
            return await e.eor("`Используйте меня в личных сообщениях.`", time=3)
        if Logm.contains(e.chat_id):
            return await e.eor("`Здесь не велось логирование сообщений.`", time=3)

        Logm.add(e.chat_id)
        return await e.eor("`Теперь я не буду логировать сообщения отсюда.`", time=3)

    @ultroid_bot.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private,
        ),
    )
    async def permitpm(event):
        user = await event.get_sender()
        if user.bot or user.is_self or user.verified or Logm.contains(user.id):
            return
        await event.forward_to(udB.get_key("PMLOGGROUP") or LOG_CHANNEL)


if udB.get_key("PMSETTING"):
    if udB.get_key("AUTOAPPROVE"):

        @ultroid_bot.on(
            events.NewMessage(
                outgoing=True,
                func=lambda e: e.is_private and e.out and not e.text.startswith(HNDLR),
            ),
        )
        async def autoappr(e):
            miss = await e.get_chat()
            if miss.bot or miss.is_self or miss.verified or miss.id in DEVLIST:
                return
            if keym.contains(miss.id):
                return
            keym.add(miss.id)
            await delete_pm_warn_msgs(miss.id)
            try:
                await ultroid_bot.edit_folder(miss.id, folder=0)
            except BaseException:
                pass
            try:
                await asst.edit_message(
                    LOG_CHANNEL,
                    _not_approved[miss.id],
                    f"#АвтоОдобрено : <b>Исходящее сообщение.\nПользователь : {inline_mention(miss, html=True)}</b> [<code>{miss.id}</code>]",
                    parse_mode="html",
                )
            except KeyError:
                await asst.send_message(
                    LOG_CHANNEL,
                    f"#АвтоОдобрено : <b>Исходящее сообщение.\nПользователь : {inline_mention(miss, html=True)}</b> [<code>{miss.id}</code>]",
                    parse_mode="html",
                )
            except MessageNotModifiedError:
                pass

    @ultroid_bot.on(
        events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private
            and e.sender_id not in DEVLIST
            and not e.out
            and not e.sender.bot
            and not e.sender.is_self
            and not e.sender.verified,
        )
    )
    async def permitpm(event):
        inline_pm = Redis("INLINE_PM") or False
        user = event.sender
        if not keym.contains(user.id) and event.text != UND:
            if Redis("MOVE_ARCHIVE"):
                try:
                    await ultroid_bot.edit_folder(user.id, folder=1)
                except BaseException as er:
                    LOGS.info(er)
            if event.media and not udB.get_key("DISABLE_PMDEL"):
                await event.delete()
            name = user.first_name
            fullname = get_display_name(user)
            username = f"@{user.username}"
            mention = inline_mention(user)
            count = keym.count()
            try:
                wrn = COUNT_PM[user.id] + 1
                await asst.edit_message(
                    udB.get_key("LOG_CHANNEL"),
                    _not_approved[user.id],
                    f"Входящее ЛС от **{mention}** [`{user.id}`] с **{wrn}/{WARNS}** предупреждением!",
                    buttons=[
                        Button.inline("Одобрить ЛС", data=f"approve_{user.id}"),
                        Button.inline("Заблокировать ЛС", data=f"block_{user.id}"),
                    ],
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"Входящее ЛС от **{mention}** [`{user.id}`] с **1/{WARNS}** предупреждением!",
                    buttons=[
                        Button.inline("Одобрить ЛС", data=f"approve_{user.id}"),
                        Button.inline("Заблокировать ЛС", data=f"block_{user.id}"),
                    ],
                )
                wrn = 1
            except MessageNotModifiedError:
                wrn = 1
            if user.id in LASTMSG:
                prevmsg = LASTMSG[user.id]
                if event.text != prevmsg:
                    if "PMSecurity" in event.text or "**PMSecurity" in event.text:
                        return
                    await delete_pm_warn_msgs(user.id)
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    update_pm(user.id, message_, wrn)
                    if inline_pm:
                        results = await ultroid_bot.inline_query(
                            my_bot, f"ip_{user.id}"
                        )
                        try:
                            _to_delete[user.id] = await results[0].click(
                                user.id, reply_to=event.id, hide_via=True
                            )
                        except Exception as e:
                            LOGS.info(str(e))
                    elif PMPIC:
                        _to_delete[user.id] = await ultroid_bot.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await ultroid_bot.send_message(
                            user.id, message_
                        )

                else:
                    await delete_pm_warn_msgs(user.id)
                    message_ = UNAPPROVED_MSG.format(
                        ON=OWNER_NAME,
                        warn=wrn,
                        twarn=WARNS,
                        UND=UND,
                        name=name,
                        fullname=fullname,
                        username=username,
                        count=count,
                        mention=mention,
                    )
                    update_pm(user.id, message_, wrn)
                    if inline_pm:
                        try:
                            results = await ultroid_bot.inline_query(
                                my_bot, f"ip_{user.id}"
                            )
                            _to_delete[user.id] = await results[0].click(
                                user.id, reply_to=event.id, hide_via=True
                            )
                        except Exception as e:
                            LOGS.info(str(e))
                    elif PMPIC:
                        _to_delete[user.id] = await ultroid_bot.send_file(
                            user.id,
                            PMPIC,
                            caption=message_,
                        )
                    else:
                        _to_delete[user.id] = await ultroid_bot.send_message(
                            user.id, message_
                        )
                LASTMSG.update({user.id: event.text})
            else:
                await delete_pm_warn_msgs(user.id)
                message_ = UNAPPROVED_MSG.format(
                    ON=OWNER_NAME,
                    warn=wrn,
                    twarn=WARNS,
                    UND=UND,
                    name=name,
                    fullname=fullname,
                    username=username,
                    count=count,
                    mention=mention,
                )
                update_pm(user.id, message_, wrn)
                if inline_pm:
                    try:
                        results = await ultroid_bot.inline_query(
                            my_bot, f"ip_{user.id}"
                        )
                        _to_delete[user.id] = await results[0].click(
                            user.id, reply_to=event.id, hide_via=True
                        )
                    except Exception as e:
                        LOGS.info(str(e))
                elif PMPIC:
                    _to_delete[user.id] = await ultroid_bot.send_file(
                        user.id,
                        PMPIC,
                        caption=message_,
                    )
                else:
                    _to_delete[user.id] = await ultroid_bot.send_message(
                        user.id, message_
                    )
            LASTMSG.update({user.id: event.text})
            if user.id not in COUNT_PM:
                COUNT_PM.update({user.id: 1})
            else:
                COUNT_PM[user.id] = COUNT_PM[user.id] + 1
            if COUNT_PM[user.id] >= WARNS:
                await delete_pm_warn_msgs(user.id)
                _to_delete[user.id] = await event.respond(UNS)
                try:
                    del COUNT_PM[user.id]
                    del LASTMSG[user.id]
                except KeyError:
                    await asst.send_message(
                        udB.get_key("LOG_CHANNEL"),
                        "PMPermit сломан! Пожалуйста, перезапустите бота!!",
                    )
                    return LOGS.info("COUNT_PM is messed.")
                await ultroid_bot(BlockRequest(user.id))
                await ultroid_bot(ReportSpamRequest(peer=user.id))
                await asst.edit_message(
                    udB.get_key("LOG_CHANNEL"),
                    _not_approved[user.id],
                    f"**{mention}** [`{user.id}`] был заблокирован за спам.",
                )

    @ultroid_cmd(pattern="(start|stop|clear)archive$", fullsudo=True)
    async def _(e):
        x = e.pattern_match.group(1).strip()
        if x == "start":
            udB.set_key("MOVE_ARCHIVE", "True")
            await e.eor("Теперь я буду перемещать новые неодобренные ЛС в архив", time=5)
        elif x == "stop":
            udB.set_key("MOVE_ARCHIVE", "False")
            await e.eor("Теперь я не буду перемещать новые неодобренные ЛС в архив", time=5)
        elif x == "clear":
            try:
                await e.client.edit_folder(unpack=1)
                await e.eor("Все чаты разархивированы", time=5)
            except Exception as mm:
                await e.eor(str(mm), time=5)

    @ultroid_cmd(pattern="(a|approve)(?: |$)", fullsudo=True)
    async def approvepm(apprvpm):
        if apprvpm.reply_to_msg_id:
            user = (await apprvpm.get_reply_message()).sender
        elif apprvpm.is_private:
            user = await apprvpm.get_chat()
        else:
            return await apprvpm.edit(NO_REPLY)
        if user.id in DEVLIST:
            return await eor(
                apprvpm,
                "Это аккаунт разработчика.\nАвтоматически одобрен.",
            )
        if not keym.contains(user.id):
            keym.add(user.id)
            try:
                await delete_pm_warn_msgs(user.id)
                await apprvpm.client.edit_folder(user.id, folder=0)
            except BaseException:
                pass
            await eod(
                apprvpm,
                f"<b>{inline_mention(user, html=True)}</b> <code>одобрен для ЛС!</code>",
                parse_mode="html",
            )
            try:
                await asst.edit_message(
                    udB.get_key("LOG_CHANNEL"),
                    _not_approved[user.id],
                    f"#ОДОБРЕНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>был одобрен для ЛС с вами!</code>",
                    buttons=[
                        Button.inline("Отозвать одобрение ЛС", data=f"disapprove_{user.id}"),
                        Button.inline("Заблокировать", data=f"block_{user.id}"),
                    ],
                    parse_mode="html",
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"#ОДОБРЕНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>был одобрен для ЛС с вами!</code>",
                    buttons=[
                        Button.inline("Отозвать одобрение ЛС", data=f"disapprove_{user.id}"),
                        Button.inline("Заблокировать", data=f"block_{user.id}"),
                    ],
                    parse_mode="html",
                )
            except MessageNotModifiedError:
                pass
        else:
            await apprvpm.eor("`Пользователь, возможно, уже одобрен.`", time=5)

    @ultroid_cmd(pattern="(da|disapprove)(?: |$)", fullsudo=True)
    async def disapprovepm(e):
        if e.reply_to_msg_id:
            user = (await e.get_reply_message()).sender
        elif e.is_private:
            user = await e.get_chat()
        else:
            return await e.edit(NO_REPLY)
        if user.id in DEVLIST:
            return await eor(
                e,
                "`Это аккаунт разработчика.\nНельзя отозвать одобрение.`",
            )
        if keym.contains(user.id):
            keym.remove(user.id)
            await eod(
                e,
                f"<b>{inline_mention(user, html=True)}</b> <code>Отозвано одобрение для ЛС!</code>",
                parse_mode="html",
            )
            try:
                await asst.edit_message(
                    udB.get_key("LOG_CHANNEL"),
                    _not_approved[user.id],
                    f"#ОДОБРЕНИЕ_ОТОЗВАНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>одобрение для ЛС с вами отозвано.</code>",
                    buttons=[
                        Button.inline("Одобрить ЛС", data=f"approve_{user.id}"),
                        Button.inline("Заблокировать", data=f"block_{user.id}"),
                    ],
                    parse_mode="html",
                )
            except KeyError:
                _not_approved[user.id] = await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"#ОДОБРЕНИЕ_ОТОЗВАНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>одобрение для ЛС с вами отозвано.</code>",
                    buttons=[
                        Button.inline("Одобрить ЛС", data=f"approve_{user.id}"),
                        Button.inline("Заблокировать", data=f"block_{user.id}"),
                    ],
                    parse_mode="html",
                )
            except MessageNotModifiedError:
                pass
        else:
            await eod(
                e,
                f"<b>{inline_mention(user, html=True)}</b> <code>никогда не был одобрен!</code>",
                parse_mode="html",
            )


@ultroid_cmd(pattern="block( (.*)|$)", fullsudo=True)
async def blockpm(block):
    match = block.pattern_match.group(1).strip()
    if block.reply_to_msg_id:
        user = (await block.get_reply_message()).sender_id
    elif match:
        try:
            user = await block.client.parse_id(match)
        except Exception as er:
            return await block.eor(str(er))
    elif block.is_private:
        user = block.chat_id
    else:
        return await eor(block, NO_REPLY, time=10)

    await block.client(BlockRequest(user))
    aname = await block.client.get_entity(user)
    await block.eor(f"{inline_mention(aname)} [`{user}`] `заблокирован!`")
    try:
        keym.remove(user)
    except AttributeError:
        pass
    try:
        await asst.edit_message(
            udB.get_key("LOG_CHANNEL"),
            _not_approved[user],
            f"#ЗАБЛОКИРОВАН\n\n{inline_mention(aname)} [`{user}`] был **заблокирован**.",
            buttons=[
                Button.inline("Разблокировать", data=f"unblock_{user}"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            udB.get_key("LOG_CHANNEL"),
            f"#ЗАБЛОКИРОВАН\n\n{inline_mention(aname)} [`{user}`] был **заблокирован**.",
            buttons=[
                Button.inline("Разблокировать", data=f"unblock_{user}"),
            ],
        )
    except MessageNotModifiedError:
        pass


@ultroid_cmd(pattern="unblock( (.*)|$)", fullsudo=True)
async def unblockpm(event):
    match = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if reply:
        user = reply.sender_id
    elif match:
        if match == "all":
            msg = await event.eor(get_string("com_1"))
            u_s = await event.client(GetBlockedRequest(0, 0))
            count = len(u_s.users)
            if not count:
                return await eor(msg, "__Вы никого не заблокировали...__")
            for user in u_s.users:
                await asyncio.sleep(1)
                await event.client(UnblockRequest(user.id))
            # GetBlockedRequest возвращает не более 20 пользователей за раз.
            if count < 20:
                return await eor(msg, f"__Разблокировано {count} пользователей!__")
            while u_s.users:
                u_s = await event.client(GetBlockedRequest(0, 0))
                for user in u_s.users:
                    await asyncio.sleep(3)
                    await event.client(UnblockRequest(user.id))
                count += len(u_s.users)
            return await eor(msg, f"__Разблокировано {count} пользователей.__")

        try:
            user = await event.client.parse_id(match)
        except Exception as er:
            return await event.eor(str(er))
    elif event.is_private:
        user = event.chat_id
    else:
        return await event.eor(NO_REPLY, time=10)
    try:
        await event.client(UnblockRequest(user))
        aname = await event.client.get_entity(user)
        await event.eor(f"{inline_mention(aname)} [`{user}`] `разблокирован!`")
    except Exception as et:
        return await event.eor(f"ОШИБКА - {et}")
    try:
        await asst.edit_message(
            udB.get_key("LOG_CHANNEL"),
            _not_approved[user],
            f"#РАЗБЛОКИРОВАН\n\n{inline_mention(aname)} [`{user}`] был **разблокирован**.",
            buttons=[
                Button.inline("Заблокировать", data=f"block_{user}"),
            ],
        )
    except KeyError:
        _not_approved[user] = await asst.send_message(
            udB.get_key("LOG_CHANNEL"),
            f"#РАЗБЛОКИРОВАН\n\n{inline_mention(aname)} [`{user}`] был **разблокирован**.",
            buttons=[
                Button.inline("Заблокировать", data=f"block_{user}"),
            ],
        )
    except MessageNotModifiedError:
        pass


@ultroid_cmd(pattern="listapproved$", owner=True)
async def list_approved(event):
    xx = await event.eor(get_string("com_1"))
    all = keym.get()
    if not all:
        return await xx.eor("`Вы ещё никого не одобрили!`", time=5)
    users = []
    for i in all:
        try:
            name = get_display_name(await ultroid_bot.get_entity(i))
        except BaseException:
            name = ""
        users.append([name.strip(), str(i)])
    with open("approved_pms.txt", "w") as list_appr:
        if tabulate:
            list_appr.write(
                tabulate(users, headers=["Имя пользователя", "ID пользователя"], showindex="always")
            )
        else:
            text = "".join(f"[{user[-1]}] - {user[0]}" for user in users)
            list_appr.write(text)
    await event.reply(
        f"Список пользователей, одобренных [{OWNER_NAME}](tg://user?id={OWNER_ID})",
        file="approved_pms.txt",
    )

    await xx.delete()
    remove("approved_pms.txt")


@callback(
    re.compile(
        b"approve_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def apr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid in DEVLIST:
        await event.edit("Это разработчик! Одобрено!")
    if not keym.contains(uid):
        keym.add(uid)
        try:
            await ultroid_bot.edit_folder(uid, folder=0)
        except BaseException:
            pass
        try:
            user = await ultroid_bot.get_entity(uid)
        except BaseException:
            return await event.delete()
        await event.edit(
            f"#ОДОБРЕНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>был одобрен для ЛС с вами!</code>",
            buttons=[
                [
                    Button.inline("Отозвать одобрение ЛС", data=f"disapprove_{uid}"),
                    Button.inline("Заблокировать", data=f"block_{uid}"),
                ],
            ],
            parse_mode="html",
        )
        await delete_pm_warn_msgs(uid)
        await event.answer("Одобрено.", alert=True)
    else:
        await event.edit(
            "`Пользователь, возможно, уже одобрен.`",
            buttons=[
                [
                    Button.inline("Отозвать одобрение ЛС", data=f"disapprove_{uid}"),
                    Button.inline("Заблокировать", data=f"block_{uid}"),
                ],
            ],
        )


@callback(
    re.compile(
        b"disapprove_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def disapr_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if keym.contains(uid):
        keym.remove(uid)
        try:
            user = await ultroid_bot.get_entity(uid)
        except BaseException:
            return await event.delete()
        await event.edit(
            f"#ОДОБРЕНИЕ_ОТОЗВАНО\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>одобрение для ЛС с вами отозвано!</code>",
            buttons=[
                [
                    Button.inline("Одобрить ЛС", data=f"approve_{uid}"),
                    Button.inline("Заблокировать", data=f"block_{uid}"),
                ],
            ],
            parse_mode="html",
        )
        await event.answer("Отозвано.", alert=True)
    else:
        await event.edit(
            "`Пользователь никогда не был одобрен!`",
            buttons=[
                [
                    Button.inline("Отозвать одобрение ЛС", data=f"disapprove_{uid}"),
                    Button.inline("Заблокировать", data=f"block_{uid}"),
                ],
            ],
        )


@callback(
    re.compile(
        b"block_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def blck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    try:
        await ultroid_bot(BlockRequest(uid))
    except BaseException:
        pass
    try:
        user = await ultroid_bot.get_entity(uid)
    except BaseException:
        return await event.delete()
    await event.edit(
        f"ЗАБЛОКИРОВАН\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>был заблокирован!</code>",
        buttons=Button.inline("Разблокировать", data=f"unblock_{uid}"),
        parse_mode="html",
    )
    await event.answer("Заблокирован.", alert=True)


@callback(
    re.compile(
        b"unblock_(.*)",
    ),
    from_users=[ultroid_bot.uid],
)
async def unblck_in(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    try:
        await ultroid_bot(UnblockRequest(uid))
    except BaseException:
        pass
    try:
        user = await ultroid_bot.get_entity(uid)
    except BaseException:
        return await event.delete()
    await event.edit(
        f"#РАЗБЛОКИРОВАН\n\n<b>{inline_mention(user, html=True)}</b> [<code>{user.id}</code>] <code>был разблокирован!</code>",
        buttons=Button.inline("Заблокировать", data=f"block_{uid}"),
        parse_mode="html",
    )
    await event.answer("Разблокирован.", alert=True)


@callback("deletedissht")
async def ytfuxist(e):
    try:
        await e.answer("Удалено.")
        await e.delete()
    except BaseException:
        await ultroid_bot.delete_messages(e.chat_id, e.id)


@in_pattern(re.compile("ip_(.*)"), owner=True)
async def in_pm_ans(event):
    from_user = int(event.pattern_match.group(1).strip())
    try:
        warns = U_WARNS[from_user]
    except Exception as e:
        LOGS.info(e)
        warns = "?"
    try:
        msg_ = WARN_MSGS[from_user]
    except KeyError:
        msg_ = "**Безопасность ЛС от {OWNER_NAME}**"
    wrns = f"{warns}/{WARNS}"
    buttons = [
        [
            Button.inline("Предупреждения", data=f"admin_only{from_user}"),
            Button.inline(wrns, data=f"don_{wrns}"),
        ]
    ]
    include_media = True
    mime_type, res = None, None
    cont = None
    try:
        ext = PMPIC.split(".")[-1].lower()
    except (AttributeError, IndexError):
        ext = None
    if ext in ["img", "jpg", "png"]:
        _type = "photo"
        mime_type = "image/jpg"
    elif ext in ["mp4", "mkv", "gif"]:
        mime_type = "video/mp4"
        _type = "gif"
    else:
        try:
            res = resolve_bot_file_id(PMPIC)
        except ValueError:
            pass
        if res:
            res = [
                await event.builder.document(
                    res,
                    title="Встроенный PmPermit",
                    description="~ @TeamTeleFriend",
                    text=msg_,
                    buttons=buttons,
                    link_preview=False,
                )
            ]
        else:
            _type = "article"
            include_media = False
    if not res:
        if include_media:
            cont = types.InputWebDocument(PMPIC, 0, mime_type, [])
        res = [
            event.builder.article(
                title="Встроенный PMPermit.",
                type=_type,
                text=msg_,
                description="@TeamTeleFriend",
                include_media=include_media,
                buttons=buttons,
                thumb=cont,
                content=cont,
            )
        ]
    await event.answer(res, switch_pm="• TeleFriend •", switch_pm_param="start")


@callback(re.compile("admin_only(.*)"), from_users=[ultroid_bot.uid])
async def _admin_tools(event):
    chat = int(event.pattern_match.group(1).strip())
    await event.edit(
        buttons=[
            [
                Button.inline("Одобрить ЛС", data=f"approve_{chat}"),
                Button.inline("Заблокировать ЛС", data=f"block_{chat}"),
            ],
            [Button.inline("« Назад", data=f"pmbk_{chat}")],
        ],
    )


@callback(re.compile("don_(.*)"))
async def _mejik(e):
    data = e.pattern_match.group(1).strip().decode("utf-8").split("/")
    text = "👮‍♂ Количество предупреждений : " + data[0]
    text += "\n🤖 Общее количество предупреждений : " + data[1]
    await e.answer(text, alert=True)


@callback(re.compile("pmbk_(.*)"))
async def edt(event):
    from_user = int(event.pattern_match.group(1).strip())
    try:
        warns = U_WARNS[from_user]
    except Exception as e:
        LOGS.info(str(e))
        warns = "0"
    wrns = f"{warns}/{WARNS}"
    await event.edit(
        buttons=[
            [
                Button.inline("Предупреждения", data=f"admin_only{from_user}"),
                Button.inline(wrns, data=f"don_{wrns}"),
            ]
        ],
    )