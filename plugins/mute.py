"""
✘ Доступные команды -

• `{i}mute <ответ на сообщение/ id пользователя>`
    Заглушить пользователя в текущем чате.

• `{i}unmute <ответ на сообщение/ id пользователя>`
    Снять заглушку с пользователя в текущем чате.

• `{i}dmute <ответ на сообщение/ id пользователя>`
    Заглушить пользователя в текущем чате, удаляя сообщения.

• `{i}undmute <ответ на сообщение/ id пользователя>`
    Снять заглушку с пользователя, заглушенного через dmute, в текущем чате.

• `{i}tmute <время> <ответ на сообщение/ id пользователя>`
    с- секунды
    м- минуты
    ч- часы
    д- дни
    Заглушить пользователя в текущем чате на время.
"""
from telethon import events
from telethon.utils import get_display_name

from pyUltroid.dB.mute_db import is_muted, mute, unmute
from pyUltroid.fns.admins import ban_time

from . import asst, eod, get_string, inline_mention, ultroid_bot, ultroid_cmd


@ultroid_bot.on(events.NewMessage(incoming=True))
async def watcher(event):
    if is_muted(event.chat_id, event.sender_id):
        await event.delete()
    if event.via_bot and is_muted(event.chat_id, event.via_bot_id):
        await event.delete()


@ultroid_cmd(
    pattern="dmute( (.*)|$)",
)
async def startmute(event):
    xx = await event.eor("`Заглушение...`")
    if input_ := event.pattern_match.group(1).strip():
        try:
            userid = await event.client.parse_id(input_)
        except Exception as x:
            return await xx.edit(str(x))
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        userid = reply.sender_id
        if reply.out or userid in [ultroid_bot.me.id, asst.me.id]:
            return await xx.eor("`Вы не можете заглушить себя или своего ассистента-бота.`")
    elif event.is_private:
        userid = event.chat_id
    else:
        return await xx.eor("`Ответьте на сообщение пользователя или укажите его userid.`", time=5)
    chat = await event.get_chat()
    if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
        if not chat.admin_rights.delete_messages:
            return await xx.eor("`Недостаточно прав администратора...`", time=5)
    elif "creator" not in vars(chat) and not event.is_private:
        return await xx.eor("`Недостаточно прав администратора...`", time=5)
    if is_muted(event.chat_id, userid):
        return await xx.eor("`Этот пользователь уже заглушен в этом чате.`", time=5)
    mute(event.chat_id, userid)
    await xx.eor("`Успешно заглушен...`", time=3)


@ultroid_cmd(
    pattern="undmute( (.*)|$)",
)
async def endmute(event):
    xx = await event.eor("`Снятие заглушки...`")
    if input_ := event.pattern_match.group(1).strip():
        try:
            userid = await event.client.parse_id(input_)
        except Exception as x:
            return await xx.edit(str(x))
    elif event.reply_to_msg_id:
        userid = (await event.get_reply_message()).sender_id
    elif event.is_private:
        userid = event.chat_id
    else:
        return await xx.eor("`Ответьте на сообщение пользователя или укажите его userid.`", time=5)
    if not is_muted(event.chat_id, userid):
        return await xx.eor("`Этот пользователь не заглушен в этом чате.`", time=3)
    unmute(event.chat_id, userid)
    await xx.eor("`Успешно снята заглушка...`", time=3)


@ultroid_cmd(
    pattern="tmute",
    groups_only=True,
    manager=True,
)
async def _(e):
    xx = await e.eor("`Заглушение...`")
    huh = e.text.split()
    try:
        tme = huh[1]
    except IndexError:
        return await xx.eor("`Время заглушения?`", time=5)
    try:
        input_ = huh[2]
    except IndexError:
        input_ = ""
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        reply = await e.get_reply_message()
        userid = reply.sender_id
        name = (await reply.get_sender()).first_name
    elif input_:
        userid = await e.client.parse_id(input_)
        name = (await e.client.get_entity(userid)).first_name
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    if userid == ultroid_bot.uid:
        return await xx.eor("`Я не могу заглушить себя.`", time=3)
    try:
        bun = ban_time(tme)
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=bun,
            send_messages=False,
        )
        await eod(
            xx,
            f"`Успешно заглушен` [{name}](tg://user?id={userid}) `в {chat.title} на {tme}`",
            time=5,
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)


@ultroid_cmd(
    pattern="unmute( (.*)|$)",
    admins_only=True,
    manager=True,
)
async def _(e):
    xx = await e.eor("`Снятие заглушки...`")
    input = e.pattern_match.group(1).strip()
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        reply = await e.get_reply_message()
        userid = reply.sender_id
        name = (await reply.get_sender()).first_name
    elif input:
        userid = await e.client.parse_id(input)
        name = (await e.client.get_entity(userid)).first_name
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=True,
        )
        await eod(
            xx,
            f"`Успешно снята заглушка` [{name}](tg://user?id={userid}) `в {chat.title}`",
            time=5,
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)


@ultroid_cmd(
    pattern="mute( (.*)|$)", admins_only=True, manager=True, require="ban_users"
)
async def _(e):
    xx = await e.eor("`Заглушение...`")
    input = e.pattern_match.group(1).strip()
    chat = await e.get_chat()
    if e.reply_to_msg_id:
        userid = (await e.get_reply_message()).sender_id
        name = get_display_name(await e.client.get_entity(userid))
    elif input:
        try:
            userid = await e.client.parse_id(input)
            name = inline_mention(await e.client.get_entity(userid))
        except Exception as x:
            return await xx.edit(str(x))
    else:
        return await xx.eor(get_string("tban_1"), time=3)
    if userid == ultroid_bot.uid:
        return await xx.eor("`Я не могу заглушить себя.`", time=3)
    try:
        await e.client.edit_permissions(
            chat.id,
            userid,
            until_date=None,
            send_messages=False,
        )
        await eod(
            xx,
            f"`Успешно заглушен` {name} `в {chat.title}`",
        )
    except BaseException as m:
        await xx.eor(f"`{m}`", time=5)
