import asyncio
import inspect
import re
import sys
from io import BytesIO
from pathlib import Path
from time import gmtime, strftime
from traceback import format_exc

from telethon import Button
from telethon import __version__ as telever
from telethon import events
from telethon.errors.common import AlreadyInConversationError
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    BotInlineDisabledError,
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserIsBotError,
)
from telethon.events import MessageEdited, NewMessage
from telethon.utils import get_display_name

from pyUltroid.exceptions import DependencyMissingError
from strings import get_string

from .. import *
from .. import _ignore_eval
from ..dB import DEVLIST
from ..dB._core import LIST, LOADED
from ..fns.admins import admin_check
from ..fns.helper import bash
from ..fns.helper import time_formatter as tf
from ..version import __version__ as pyver
from ..version import ultroid_version as ult_ver
from . import SUDO_M, owner_and_sudos
from ._wrappers import eod

MANAGER = udB.get_key("MANAGER")
TAKE_EDITS = udB.get_key("TAKE_EDITS")
black_list_chats = udB.get_key("BLACKLIST_CHATS")
allow_sudo = SUDO_M.should_allow_sudo


def compile_pattern(data, hndlr):
    if data.startswith("^"):
        data = data[1:]
    if data.startswith("."):
        data = data[1:]
    if hndlr in [" ", "NO_HNDLR"]:
        # Без Hndlr
        return re.compile("^" + data)
    return re.compile("\\" + hndlr + data)


def ultroid_cmd(
    pattern=None, manager=False, ultroid_bot=ultroid_bot, asst=asst, **kwargs
):
    owner_only = kwargs.get("owner_only", False)
    groups_only = kwargs.get("groups_only", False)
    admins_only = kwargs.get("admins_only", False)
    fullsudo = kwargs.get("fullsudo", False)
    only_devs = kwargs.get("only_devs", False)
    func = kwargs.get("func", lambda e: not e.via_bot_id)

    def decor(dec):
        async def wrapp(ult):
            if udB.get_key("COMMAND_LOGGER"):
                user_id = ult.sender_id
                chat_id = ult.chat_id
                command_name = pattern if pattern else ult.text.split()[0].lstrip(HNDLR)
                chat_name = get_display_name(ult.chat)
                LOGS.info(f"Команда '{command_name}' выполнена пользователем с ID {user_id} в чате {chat_id} ({chat_name})")
                log_channel = udB.get_key("LOG_CHANNEL")
                if log_channel:
                    try:
                        await asst.send_message(
                            log_channel,
                            f"Команда '{command_name}' выполнена пользователем с ID {user_id} в чате {chat_id} ({chat_name})"
                        )
                    except Exception as e:
                        LOGS.warning(f"Не удалось отправить лог команды в канал {log_channel}: {e}")
            if not ult.out:
                if owner_only:
                    return
                if ult.sender_id not in owner_and_sudos():
                    return
                if ult.sender_id in _ignore_eval:
                    return await eod(
                        ult,
                        get_string("py_d1"),
                    )
                if fullsudo and ult.sender_id not in SUDO_M.fullsudos:
                    return await eod(ult, get_string("py_d2"), time=15)
            chat = ult.chat
            if hasattr(chat, "title"):
                if (
                    "#noub" in chat.title.lower()
                    and not (chat.admin_rights or chat.creator)
                    and not (ult.sender_id in DEVLIST)
                ):
                    return
            if ult.is_private and (groups_only or admins_only):
                return await eod(ult, get_string("py_d3"))
            elif admins_only and not (chat.admin_rights or chat.creator):
                return await eod(ult, get_string("py_d5"))
            if only_devs and not udB.get_key("I_DEV"):
                return await eod(
                    ult,
                    get_string("py_d4").format(HNDLR),
                    time=10,
                )
            try:
                await dec(ult)
            except FloodWaitError as fwerr:
                await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    f"\`FloodWaitError:\n{str(fwerr)}\n\nСплю {tf((fwerr.seconds + 10)*1000)}\`",
                )
                await ultroid_bot.disconnect()
                await asyncio.sleep(fwerr.seconds + 10)
                await ultroid_bot.connect()
                await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    "\`Бот снова работает\`",
                )
                return
            except ChatSendInlineForbiddenError:
                return await eod(ult, "\`Инлайн заблокирован в этом чате.\`")
            except (ChatSendMediaForbiddenError, ChatSendStickersForbiddenError):
                return await eod(ult, get_string("py_d8"))
            except (BotMethodInvalidError, UserIsBotError):
                return await eod(ult, get_string("py_d6"))
            except AlreadyInConversationError:
                return await eod(
                    ult,
                    get_string("py_d7"),
                )
            except (BotInlineDisabledError, DependencyMissingError) as er:
                return await eod(ult, f"\`{er}\`")
            except (
                MessageIdInvalidError,
                MessageNotModifiedError,
                MessageDeleteForbiddenError,
            ) as er:
                LOGS.exception(er)
            except AuthKeyDuplicatedError as er:
                LOGS.exception(er)
                await asst.send_message(
                    udB.get_key("LOG_CHANNEL"),
                    "Строка сессии истекла, создайте новую сессию отсюда 👇",
                    buttons=[
                        Button.url("Bot", "t.me/SessionGeneratorBot?start="),
                        Button.url(
                            "Repl",
                            "https://replit.com/@TheTeleFriend/TeleFriendStringSession",
                        ),
                    ],
                )
                sys.exit()
            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except Exception as e:
                LOGS.exception(e)
                date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                naam = get_display_name(chat)
                ftext = f"**Ошибка клиента TeleFriend:** \`Перешлите это\` @TeleFriendSupportChat\n\n"
                ftext += f"**Версия Py-TeleFriend:** \`" + str(pyver)
                ftext += f"\`\n**Версия TeleFriend:** \`" + str(ult_ver)
                ftext += f"\`\n**Версия Telethon:** \`" + str(telever)
                ftext += f"\`\n**Хостится на:** \`{HOSTED_ON}\n\n"
                ftext += "--------НАЧАЛО ЛОГА АВАРИИ ULTROID--------"
                ftext += "\n**Дата:** \`" + date
                ftext += "\`\n**Группа:** \`" + str(ult.chat_id) + "\` " + str(naam)
                ftext += "\n**ID отправителя:** \`" + str(ult.sender_id)
                ftext += "\`\n**Ответ:** \`" + str(ult.is_reply)
                ftext += "\`\n\n**Событие-триггер:**\`\n"
                ftext += str(ult.text)
                ftext += "\`\n\n**Информация о трассировке:**\`\n"
                ftext += str(format_exc())
                ftext += "\`\n\n**Текст ошибки:**\`\n"
                ftext += str(sys.exc_info()[1])
                ftext += "\`\n\n--------КОНЕЦ ЛОГА АВАРИИ ULTROID--------"
                ftext += "\n\n\n**Последние 5 коммитов:**\`\n"

                stdout, stderr = await bash('git log --pretty=format:"%an: %s" -5')
                result = stdout + (stderr or "")

                ftext += f"{result}\`"

                if len(ftext) > 4096:
                    with BytesIO(ftext.encode()) as file:
                        file.name = "logs.txt"
                        error_log = await asst.send_file(
                            udB.get_key("LOG_CHANNEL"),
                            file,
                            caption="**Ошибка клиента TeleFriend:** \`Перешлите это\` @TeleFriendSupportChat\n\n",
                        )
                else:
                    error_log = await asst.send_message(
                        udB.get_key("LOG_CHANNEL"),
                        ftext,
                    )
                if ult.out:
                    await ult.edit(
                        f"<b><a href={error_log.message_link}>[Произошла ошибка]</a></b>",
                        link_preview=False,
                        parse_mode="html",
                    )

        cmd = None
        blacklist_chats = False
        chats = None
        if black_list_chats:
            blacklist_chats = True
            chats = list(black_list_chats)
        _add_new = allow_sudo and HNDLR != SUDO_HNDLR
        if _add_new:
            if pattern:
                cmd = compile_pattern(pattern, SUDO_HNDLR)
            ultroid_bot.add_event_handler(
                wrapp,
                NewMessage(
                    pattern=cmd,
                    incoming=True,
                    forwards=False,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if pattern:
            cmd = compile_pattern(pattern, HNDLR)
        ultroid_bot.add_event_handler(
            wrapp,
            NewMessage(
                outgoing=True if _add_new else None,
                pattern=cmd,
                forwards=False,
                func=func,
                chats=chats,
                blacklist_chats=blacklist_chats,
            ),
        )
        if TAKE_EDITS:

            def func_(x):
                return not x.via_bot_id and not (x.is_channel and x.chat.broadcast)

            ultroid_bot.add_event_handler(
                wrapp,
                MessageEdited(
                    pattern=cmd,
                    forwards=False,
                    func=func_,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if manager and MANAGER:
            allow_all = kwargs.get("allow_all", False)
            allow_pm = kwargs.get("allow_pm", False)
            require = kwargs.get("require", None)

            async def manager_cmd(ult):
                if not allow_all and not (await admin_check(ult, require=require)):
                    return
                if not allow_pm and ult.is_private:
                    return
                try:
                    await dec(ult)
                except Exception as er:
                    if chat := udB.get_key("MANAGER_LOG"):
                        text = f"\*\*#МЕНЕДЖЕР_ЛОГ\n\nЧат:\*\* \`{get_display_name(ult.chat)}\` \`{ult.chat_id}\`"
                        text += f"\n\*\*Ответ :\*\* \`{ult.is_reply}\`\n\*\*Команда :\*\* {ult.text}\n\n\*\*Ошибка :\*\* \`{er}\`"
                        try:
                            return await asst.send_message(
                                chat, text, link_preview=False
                            )
                        except Exception as er:
                            LOGS.exception(er)
                    LOGS.info(f"• МЕНЕДЖЕР [{ult.chat_id}]:")
                    LOGS.exception(er)

            if pattern:
                cmd = compile_pattern(pattern, "/")
            asst.add_event_handler(
                manager_cmd,
                NewMessage(
                    pattern=cmd,
                    forwards=False,
                    incoming=True,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        if DUAL_MODE and not (manager and DUAL_HNDLR == "/"):
            if pattern:
                cmd = compile_pattern(pattern, DUAL_HNDLR)
            asst.add_event_handler(
                wrapp,
                NewMessage(
                    pattern=cmd,
                    incoming=True,
                    forwards=False,
                    func=func,
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                ),
            )
        file = Path(inspect.stack()[1].filename)
        if "addons/" in str(file):
            if LOADED.get(file.stem):
                LOADED[file.stem].append(wrapp)
            else:
                LOADED.update({file.stem: [wrapp]})
        if pattern:
            if LIST.get(file.stem):
                LIST[file.stem].append(pattern)
            else:
                LIST.update({file.stem: [pattern]})
        return wrapp

    return decor
