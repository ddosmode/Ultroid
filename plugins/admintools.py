from . import get_help

__doc__ = get_help("help_admintools")

import asyncio

from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import ChatNotModifiedError, UserIdInvalidError
from telethon.tl.functions.channels import EditAdminRequest, GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest, SetHistoryTTLRequest
from telethon.tl.types import InputMessagesFilterPinned
from telethon.utils import get_display_name

from pyUltroid.dB import DEVLIST
from pyUltroid.fns.admins import ban_time
from pyUltroid.fns.info import get_uinfo

from . import HNDLR, LOGS, eod, eor, get_string, inline_mention, types, ultroid_cmd


@ultroid_cmd(
    pattern="promote( (.*)|$)",
    admins_only=True,
    manager=True,
    require="add_admins",
    fullsudo=True,
)
async def prmte(ult):
    xx = await ult.eor(get_string("com_1"))
    user, rank = await get_uinfo(ult)
    rank = rank or "Админ"
    FullRight = False
    if not user:
        return await xx.edit(get_string("pro_1"))
    if rank.split()[0] == "-f":
        try:
            rank = rank.split(maxsplit=1)[1]
        except IndexError:
            rank = "Админ"
        FullRight = True
    try:
        if FullRight:
            await ult.client(
                EditAdminRequest(ult.chat_id, user.id, ult.chat.admin_rights, rank)
            )
        else:
            await ult.client.edit_admin(
                ult.chat_id,
                user.id,
                invite_users=True,
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                manage_call=True,
                title=rank,
            )
        await eod(
            xx, get_string("pro_2").format(inline_mention(user), ult.chat.title, rank)
        )
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="demote( (.*)|$)",
    admins_only=True,
    manager=True,
    require="add_admins",
    fullsudo=True,
)
async def dmote(ult):
    xx = await ult.eor(get_string("com_1"))
    user, rank = await get_uinfo(ult)
    if not rank:
        rank = "Не админ"
    if not user:
        return await xx.edit(get_string("de_1"))
    try:
        await ult.client.edit_admin(
            ult.chat_id,
            user.id,
            invite_users=None,
            ban_users=None,
            delete_messages=None,
            pin_messages=None,
            manage_call=None,
            title=rank,
        )
        await eod(xx, get_string("de_2").format(inline_mention(user), ult.chat.title))
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="ban( (.*)|$)",
    admins_only=True,
    manager=True,
    require="ban_users",
    fullsudo=True,
)
async def ban_user(ult):
    xx = await ult.eor(get_string("com_1"))
    user, reason = await get_uinfo(ult, get_reason=True)
    if not user:
        return await xx.edit(get_string("ban_1"))
    if user.id in DEVLIST:
        return await xx.edit(get_string("ban_2"))
    if not ult.chat.admin_rights:
        return await xx.edit(get_string("ban_3"))
    try:
        await ult.client.edit_permissions(
            ult.chat_id,
            user.id,
            view_messages=False,
        )
        ban_reason = reason or "Без причины"
        ban_text = get_string("ban_4").format(inline_mention(user), inline_mention(ult.sender), ult.chat.title)
        if reason:
            ban_text += get_string("ban_5").format(reason)
        await xx.edit(ban_text)
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="unban( (.*)|$)",
    admins_only=True,
    manager=True,
    require="ban_users",
    fullsudo=True,
)
async def unban_user(ult):
    xx = await ult.eor(get_string("com_1"))
    user, _ = await get_uinfo(ult)
    if not user:
        return await xx.edit(get_string("unban_1"))
    if not ult.chat.admin_rights:
        return await xx.edit(get_string("unban_2"))
    try:
        await ult.client.edit_permissions(
            ult.chat_id,
            user.id,
            view_messages=True,
        )
        await xx.edit(get_string("unban_3").format(inline_mention(user), inline_mention(ult.sender), ult.chat.title))
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(
    pattern="kick( (.*)|$)",
    admins_only=True,
    manager=True,
    require="kick_users",
    fullsudo=True,
)
async def kick_user(ult):
    xx = await ult.eor(get_string("com_1"))
    user, _ = await get_uinfo(ult)
    if not user:
        return await xx.edit(get_string("kick_3"))
    if user.id in DEVLIST:
        return await xx.edit(get_string("kick_2"))
    if not ult.chat.admin_rights:
        return await xx.edit(get_string("kick_1"))
    try:
        await ult.client.kick_participant(ult.chat_id, user.id)
        await xx.edit(get_string("kick_4").format(inline_mention(user), inline_mention(ult.sender), ult.chat.title))
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(pattern="pin( (.*)|$)", admins_only=True, manager=True)
async def pin_msg(ult):
    xx = await ult.eor(get_string("com_1"))
    if not ult.reply_to_msg_id:
        return await xx.edit(get_string("pin_1"))
    try:
        await ult.client.pin_message(ult.chat_id, ult.reply_to_msg_id, notify=True)
        await xx.edit("Сообщение закреплено!")
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(pattern="unpin( (.*)|$)", admins_only=True, manager=True)
async def unpin_msg(ult):
    xx = await ult.eor(get_string("com_1"))
    if not ult.reply_to_msg_id:
        return await xx.edit(get_string("unpin_1"))
    try:
        await ult.client.unpin_message(ult.chat_id, ult.reply_to_msg_id)
        await xx.edit("Сообщение откреплено!")
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(pattern="purge( (.*)|$)", admins_only=True, manager=True)
async def purge_msgs(ult):
    xx = await ult.eor(get_string("com_1"))
    if not ult.reply_to_msg_id:
        return await xx.edit(get_string("purge_1"))
    try:
        await ult.client.purge(ult.chat_id, ult.reply_to_msg_id)
        await xx.edit("Сообщения удалены!")
    except Exception as ex:
        return await xx.edit(f"`{ex}`")


@ultroid_cmd(pattern="purgeall", admins_only=True, manager=True)
async def purge_all(ult):
    xx = await ult.eor(get_string("com_1"))
    if not ult.reply_to_msg_id:
        return await xx.edit(get_string("purgeall_1"))
    try:
        await ult.client.purge(ult.chat_id, purge_all=True)
        await xx.edit(get_string("purgeall_2").format(ult.chat.title))
    except Exception as ex:
        return await xx.edit(f"`{ex}`")
