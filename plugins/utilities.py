# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}kickme` : Покинуть группу.

• `{i}date` : Показать календарь.

• `{i}listreserved`
    Показать все имена пользователей (каналы/группы), которыми вы владеете.

• `{i}stats` : Посмотреть статистику вашего профиля.

• `{i}paste` - `Вставить длинный текст / Ответить на текстовый файл.`

• `{i}info <имя пользователя/id пользователя/id чата>`
    Ответьте на сообщение кого-либо.

• `{i}invite <имя пользователя/id пользователя>`
    Добавить пользователя в чат.

• `{i}rmbg <ответ на фото>`
    Убрать фон с этой картинки.

• `{i}telegraph <ответ на медиа/текст>`
    Загрузить медиа/текст в Telegraph.

• `{i}json <ответ на сообщение>`
    Получить JSON-кодировку сообщения.

• `{i}suggest <ответ на сообщение> или <заголовок опроса>`
    Создать опрос Да/Нет для предложения, на которое ответили.

• `{i}ipinfo <ip-адрес>` : Получить информацию об этом IP-адресе.

• `{i}cpy <ответ на сообщение>`
   Скопировать ответное сообщение с форматированием. Истекает через 24 часа.
• `{i}pst`
   Вставить скопированное сообщение с форматированием.

• `{i}thumb <ответ на файл>` : Скачать миниатюру ответного файла.

• `{i}getmsg <ссылка на сообщение>`
  Получить сообщения из чатов с ограничениями на пересылку/копирование.
"""

import asyncio
import calendar
import html
import io
import os
import pathlib
import time
from datetime import datetime as dt

try:
    from PIL import Image
except ImportError:
    Image = None

from pyUltroid._misc._assistant import asst_cmd
from pyUltroid.dB.gban_mute_db import is_gbanned
from pyUltroid.fns.tools import get_chat_and_msgid

from . import upload_file as uf

from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError, UserBotError
from telethon.errors import MessageTooLongError
from telethon.events import NewMessage
from telethon.tl.custom import Dialog
from telethon.tl.functions.channels import (
    GetAdminedPublicChannelsRequest,
    InviteToChannelRequest,
    LeaveChannelRequest,
)
from telethon.tl.functions.contacts import GetBlockedRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetAllStickersRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    Channel,
    Chat,
    InputMediaPoll,
    Poll,
    PollAnswer,
    TLObject,
    User,
    UserStatusOffline,
    UserStatusOnline,
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
)
from telethon.utils import get_peer_id

from pyUltroid.fns.info import get_chat_info

from . import (
    HNDLR,
    LOGS,
    Image,
    ReTrieveFile,
    Telegraph,
    asst,
    async_searcher,
    bash,
    check_filename,
    eod,
    eor,
    get_paste,
    get_string,
    inline_mention,
    json_parser,
    mediainfo,
    udB,
    ultroid_cmd,
)

# =================================================================#

TMP_DOWNLOAD_DIRECTORY = "resources/downloads/"

CAPTION_LIMIT = 1024  # Лимит символов подписи Telegram для не-премиум

_copied_msg = {}


@ultroid_cmd(pattern="kickme$", fullsudo=True)
async def leave(ult):
    await ult.eor(f"`{ult.client.me.first_name} покинул эту группу, пока!!.`")
    await ult.client(LeaveChannelRequest(ult.chat_id))


@ultroid_cmd(
    pattern="date$",
)
async def date(event):
    m = dt.now().month
    y = dt.now().year
    d = dt.now().strftime("Дата - %B %d, %Y\nВремя- %H:%M:%S")
    k = calendar.month(y, m)
    await event.eor(f"`{k}\n\n{d}`")


@ultroid_cmd(
    pattern="listreserved$",
)
async def _(event):
    result = await event.client(GetAdminedPublicChannelsRequest())
    if not result.chats:
        return await event.eor("`Нет зарезервированных имён пользователей`")
    output_str = "".join(
        f"- {channel_obj.title} @{channel_obj.username} \n"
        for channel_obj in result.chats
    )
    await event.eor(output_str)


@ultroid_cmd(
    pattern="stats$",
)
async def stats(
    event: NewMessage.Event,
):
    ok = await event.eor("`Сбор статистики...`")
    start_time = time.time()
    private_chats = 0
    bots = 0
    groups = 0
    broadcast_channels = 0
    admin_in_groups = 0
    creator_in_groups = 0
    admin_in_broadcast_channels = 0
    creator_in_channels = 0
    unread_mentions = 0
    unread = 0
    dialog: Dialog
    async for dialog in event.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:
            broadcast_channels += 1
            if entity.creator or entity.admin_rights:
                admin_in_broadcast_channels += 1
            if entity.creator:
                creator_in_channels += 1

        elif (isinstance(entity, Channel) and entity.megagroup) or isinstance(
            entity, Chat
        ):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1

        elif isinstance(entity, User):
            private_chats += 1
            if entity.bot:
                bots += 1

        unread_mentions += dialog.unread_mentions_count
        unread += dialog.unread_count
    stop_time = time.time() - start_time
    try:
        ct = (await event.client(GetBlockedRequest(1, 0))).count
    except AttributeError:
        ct = 0
    try:
        sp = await event.client(GetAllStickersRequest(0))
        sp_count = len(sp.sets)
    except BaseException:
        sp_count = 0
    full_name = inline_mention(event.client.me)
    response = f"🔸 **Статистика для {full_name}** \n\n"
    response += f"**Личные чаты:** {private_chats} \n"
    response += f"**  •• **`Пользователи: {private_chats - bots}` \n"
    response += f"**  •• **`Боты: {bots}` \n"
    response += f"**Группы:** {groups} \n"
    response += f"**Каналы:** {broadcast_channels} \n"
    response += f"**Админ в группах:** {admin_in_groups} \n"
    response += f"**  •• **`Создатель: {creator_in_groups}` \n"
    response += f"**  •• **`Права админа: {admin_in_groups - creator_in_groups}` \n"
    response += f"**Админ в каналах:** {admin_in_broadcast_channels} \n"
    response += f"**  •• **`Создатель: {creator_in_channels}` \n"
    response += f"**  •• **`Права админа: {admin_in_broadcast_channels - creator_in_channels}` \n"
    response += f"**Непрочитано:** {unread} \n"
    response += f"**Непрочитанные упоминания:** {unread_mentions} \n"
    response += f"**Заблокированные пользователи:** {ct}\n"
    response += f"**Всего наборов стикеров установлено :** `{sp_count}`\n\n"
    response += f"**__Затрачено времени:__** {stop_time:.02f}s \n"
    await ok.edit(response)


@ultroid_cmd(pattern="paste( (.*)|$)", manager=True, allow_all=True)
async def _(event):
    try:
        input_str = event.text.split(maxsplit=1)[1]
    except IndexError:
        input_str = None
    xx = await event.eor("` 《 Вставка... 》 `")
    downloaded_file_name = None
    if input_str:
        message = input_str
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message,
                "./resources/downloads",
            )
            with open(downloaded_file_name, "r") as fd:
                message = fd.read()
            os.remove(downloaded_file_name)
        else:
            message = previous_message.message
    else:
        message = None
    if not message:
        return await xx.eor(
            "`Ответьте на сообщение/документ или дайте мне текст!`", time=5
        )
    done, data = await get_paste(message)
    if not done and data.get("error"):
        return await xx.eor(data["error"])
    reply_text = (
        f"• **Вставлено в SpaceBin :** [Space]({data['link']})\n• **Сырая ссылка :** : [Raw]({data['raw']})"
    )
    try:
        if event.client._bot:
            return await xx.eor(reply_text)
        ok = await event.client.inline_query(asst.me.username, f"pasta-{data['link']}")
        await ok[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
        await xx.delete()
    except BaseException as e:
        LOGS.exception(e)
        await xx.edit(reply_text)


@ultroid_cmd(
    pattern="info( (.*)|$)",
    manager=True,
)
async def _(event):
    if match := event.pattern_match.group(1).strip():
        try:
            user = await event.client.parse_id(match)
        except Exception as er:
            return await event.eor(str(er))
    elif event.is_reply:
        rpl = await event.get_reply_message()
        user = rpl.sender_id
    else:
        user = event.chat_id
    xx = await event.eor(get_string("com_1"))
    try:
        _ = await event.client.get_entity(user)
    except Exception as er:
        return await xx.edit(f"**ОШИБКА :** {er}")
    if not isinstance(_, User):
        try:
            peer = get_peer_id(_)
            photo, capt = await get_chat_info(_, event)
            if is_gbanned(peer):
                capt += "\n•<b> Глобально забанен:</b> <code>True</code>"
            if not photo:
                return await xx.eor(capt, parse_mode="html")
            await event.client.send_message(
                event.chat_id, capt[:1024], file=photo, parse_mode="html"
            )
            await xx.delete()
        except Exception as er:
            await event.eor("**ОШИБКА В ИНФО ЧАТА**\n" + str(er))
        return
    try:
        full_user = (await event.client(GetFullUserRequest(user))).full_user
    except Exception as er:
        return await xx.edit(f"ОШИБКА : {er}")
    user = _
    user_photos = (
        await event.client.get_profile_photos(user.id, limit=0)
    ).total or "NaN"
    user_id = user.id
    first_name = html.escape(user.first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = user.last_name
    last_name = (
        last_name.replace("\u2060", "") if last_name else ("Фамилия не найдена")
    )
    user_bio = full_user.about
    if user_bio is not None:
        user_bio = html.escape(full_user.about)
    common_chats = full_user.common_chats_count
    if user.photo:
        dc_id = user.photo.dc_id
    else:
        dc_id = "Нужно фото профиля для проверки"
    caption = """<b>Извлеченные данные из базы Telegram</b>
<b>• Telegram ID</b>: <code>{}</code>
<b>• Постоянная ссылка</b>: <a href='tg://user?id={}'>Нажмите здесь</a>
<b>• Имя</b>: <code>{}</code>
<b>• Фамилия</b>: <code>{}</code>
<b>• Био</b>: <code>{}</code>
<b>• ID DC</b>: <code>{}</code>
<b>• Количество фото профиля</b>: <code>{}</code>
<b>• Ограничен</b>: <code>{}</code>
<b>• Верифицирован</b>: <code>{}</code>
<b>• Премиум</b>: <code>{}</code>
<b>• Бот</b>: <code>{}</code>
<b>• Общие группы</b>: <code>{}</code>
""".format(
        user_id,
        user_id,
        first_name,
        last_name,
        user_bio,
        dc_id,
        user_photos,
        user.restricted,
        user.verified,
        user.premium,
        user.bot,
        common_chats,
    )
    if chk := is_gbanned(user_id):
        caption += f"""<b>••ГЛОБАЛЬНО ЗАБАНЕН</b>: <code>True</code>
<b>••Причина</b>: <code>{chk}</code>"""
    await event.client.send_message(
        event.chat_id,
        caption,
        reply_to=event.reply_to_msg_id,
        parse_mode="HTML",
        file=full_user.profile_photo,
        force_document=False,
        silent=True,
    )
    await xx.delete()


@ultroid_cmd(
    pattern="invite( (.*)|$)",
    groups_only=True,
)
async def _(ult):
    xx = await ult.eor(get_string("com_1"))
    to_add_users = ult.pattern_match.group(1).strip()
    if not ult.is_channel and ult.is_group:
        for user_id in to_add_users.split(" "):
            try:
                await ult.client(
                    AddChatUserRequest(
                        chat_id=ult.chat_id,
                        user_id=await ult.client.parse_id(user_id),
                        fwd_limit=1000000,
                    ),
                )
                await xx.edit(f"Успешно приглашён `{user_id}` в `{ult.chat_id}`")
            except Exception as e:
                await xx.edit(str(e))
    else:
        for user_id in to_add_users.split(" "):
            try:
                await ult.client(
                    InviteToChannelRequest(
                        channel=ult.chat_id,
                        users=[await ult.client.parse_id(user_id)],
                    ),
                )
                await xx.edit(f"Успешно приглашён `{user_id}` в `{ult.chat_id}`")
            except UserBotError:
                await xx.edit(
                    f"Ботов можно добавлять только как администраторов в канал.\nЛучше используйте `{HNDLR}promote {user_id}`"
                )
            except Exception as e:
                await xx.edit(str(e))


@ultroid_cmd(
    pattern="rmbg($| (.*))",
)
async def abs_rmbg(event):
    RMBG_API = udB.get_key("RMBG_API")
    if not RMBG_API:
        return await event.eor(
            "Получите ваш API ключ [здесь](https://www.remove.bg/) для работы этого плагина.",
        )
    match = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if match and os.path.exists(match):
        dl = match
    elif reply and reply.media:
        if reply.document and reply.document.thumbs:
            dl = await reply.download_media(thumb=-1)
        else:
            dl = await reply.download_media()
    else:
        return await eod(
            event, f"Используйте `{HNDLR}rmbg` в ответ на фото, чтобы убрать фон."
        )
    if not (dl and dl.endswith(("webp", "jpg", "png", "jpeg"))):
        os.remove(dl)
        return await event.eor(get_string("com_4"))
    if dl.endswith("webp"):
        file = f"{dl}.png"
        Image.open(dl).save(file)
        os.remove(dl)
        dl = file
    xx = await event.eor("`Отправка в remove.bg`")
    dn, out = await ReTrieveFile(dl)
    os.remove(dl)
    if not dn:
        dr = out["errors"][0]
        de = dr.get("detail", "")
        return await xx.edit(
            f"**ОШИБКА ~** `{dr['title']}`,\n`{de}`",
        )
    zz = Image.open(out)
    if zz.mode != "RGB":
        zz.convert("RGB")
    wbn = check_filename("ult-rmbg.webp")
    zz.save(wbn, "webp")
    await event.client.send_file(
        event.chat_id,
        out,
        force_document=True,
        reply_to=reply,
    )
    await event.client.send_file(event.chat_id, wbn, reply_to=reply)
    os.remove(out)
    os.remove(wbn)
    await xx.delete()


@ultroid_cmd(
    pattern="telegraph( (.*)|$)",
)
async def telegraphcmd(event):
    xx = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1).strip() or "Ultroid"
    reply = await event.get_reply_message()
    if not reply:
        return await xx.eor("`Ответьте на сообщение.`")
    if not reply.media and reply.message:
        content = reply.message
    else:
        getit = await reply.download_media()
        dar = mediainfo(reply.media)
        if dar == "sticker":
            file = f"{getit}.png"
            Image.open(getit).save(file)
            os.remove(getit)
            getit = file
        elif dar.endswith("animated"):
            file = f"{getit}.gif"
            await bash(f"lottie_convert.py '{getit}' {file}")
            os.remove(getit)
            getit = file
        if "document" not in dar:
            try:
                nn = uf(getit)
                amsg = f"Загружено в [Telegraph]({nn}) !"
            except Exception as e:
                amsg = f"Ошибка : {e}"
            os.remove(getit)
            return await xx.eor(amsg)
        content = pathlib.Path(getit).read_text()
        os.remove(getit)
    makeit = Telegraph.create_page(title=match, content=[content])
    await xx.eor(
        f"Вставлено в Telegraph : [Telegraph]({makeit['url']})", link_preview=False
    )


@ultroid_cmd(pattern="json( (.*)|$)")
async def _(event):
    reply_to_id = None
    match = event.pattern_match.group(1).strip()
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        reply_to_id = event.reply_to_msg_id
    else:
        msg = event
        reply_to_id = event.message.id
    if match and hasattr(msg, match.split()[0]):
        msg = getattr(msg, match.split()[0])
        try:
            if hasattr(msg, "to_json"):
                msg = msg.to_json(ensure_ascii=False, indent=1)
            elif hasattr(msg, "to_dict"):
                msg = json_parser(msg.to_dict(), indent=1)
            else:
                msg = TLObject.stringify(msg)
        except Exception:
            pass
        msg = str(msg)
    else:
        msg = json_parser(msg.to_json(), indent=1)
    if "-t" in match:
        try:
            data = json_parser(msg)
            msg = json_parser(
                {key: data[key] for key in data.keys() if data[key]}, indent=1
            )
        except Exception:
            pass
    if len(msg) > 4096:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "json-ult.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await event.eor(f"```{msg or None}```")


@ultroid_cmd(pattern="suggest( (.*)|$)", manager=True)
async def sugg(event):
    sll = event.text.split(maxsplit=1)
    try:
        text = sll[1]
    except IndexError:
        text = None
    if not (event.is_reply or text):
        return await eod(
            event,
            "`Пожалуйста, ответьте на сообщение, чтобы создать опрос с предложением!`",
        )
    if event.is_reply and not text:
        reply = await event.get_reply_message()
        if reply.text and len(reply.text) < 35:
            text = reply.text
        else:
            text = "Вы согласны с предложенным вариантом ?"
    reply_to = event.reply_to_msg_id if event.is_reply else event.id
    try:
        await event.client.send_file(
            event.chat_id,
            file=InputMediaPoll(
                poll=Poll(
                    id=12345,
                    question=text,
                    answers=[PollAnswer("Да", b"1"), PollAnswer("Нет", b"2")],
                ),
            ),
            reply_to=reply_to,
        )
    except Exception as e:
        return await eod(event, f"`Упс, вы не можете отправлять опросы здесь!\n\n{e}`")
    await event.delete()


@ultroid_cmd(pattern="ipinfo( (.*)|$)")
async def ipinfo(event):
    ip = event.text.split()
    ipaddr = ""
    try:
        ipaddr = f"/{ip[1]}"
    except IndexError:
        ipaddr = ""
    det = await async_searcher(f"https://ipinfo.io{ipaddr}/geo", re_json=True)
    try:
        ip = det["ip"]
        city = det["city"]
        region = det["region"]
        country = det["country"]
        cord = det["loc"]
        try:
            zipc = det["postal"]
        except KeyError:
            zipc = "None"
        tz = det["timezone"]
        await eor(
            event,
            """
**Данные IP получены.**

**IP:** `{}`
**Город:** `{}`
**Регион:** `{}`
**Страна:** `{}`
**Координаты:** `{}`
**Почтовый индекс:** `{}`
**Часовой пояс:** `{}`
""".format(
                ip,
                city,
                region,
                country,
                cord,
                zipc,
                tz,
            ),
        )
    except BaseException:
        err = det["error"]["title"]
        msg = det["error"]["message"]
        await event.eor(f"ОШИБКА:\n{err}\n{msg}", time=5)


@ultroid_cmd(
    pattern="cpy$",
)
async def copp(event):
    msg = await event.get_reply_message()
    if not msg:
        return await event.eor(f"Используйте `{HNDLR}cpy` в ответ на сообщение!", time=5)
    _copied_msg["CLIPBOARD"] = msg
    await event.eor(f"Скопировано. Используйте `{HNDLR}pst` для вставки!", time=10)


@asst_cmd(pattern="pst$")
async def pepsodent(event):
    await toothpaste(event)


@ultroid_cmd(
    pattern="pst$",
)
async def colgate(event):
    await toothpaste(event)


async def toothpaste(event):
    try:
        await event.respond(_copied_msg["CLIPBOARD"])
    except KeyError:
        return await eod(
            event,
            f"Ничего не скопировано! Сначала используйте `{HNDLR}cpy` в ответ на сообщение!",
        )
    except Exception as ex:
        return await event.eor(str(ex), time=5)
    await event.delete()


@ultroid_cmd(pattern="thumb$")
async def thumb_dl(event):
    reply = await event.get_reply_message()
    if not (reply and reply.file):
        return await eod(event, get_string("th_1"), time=5)
    if not reply.file.media.thumbs:
        return await eod(event, get_string("th_2"))
    await event.eor(get_string("com_1"))
    x = await event.get_reply_message()
    m = await x.download_media(thumb=-1)
    await event.reply(file=m)
    os.remove(m)


async def get_video_duration(file_path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    try:
        result = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        duration = float(stdout.decode().strip())
        return duration
    except Exception as e:
        print("Ошибка запуска ffprobe:", e)
        return None

async def get_thumbnail(file_path, thumbnail_path):
    try:
        await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", file_path,
            "-ss", "00:00:04",
            "-vframes", "1",  # Извлечь один кадр в качестве миниатюры
            thumbnail_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        print(f"Ошибка извлечения миниатюры: {e}")

@ultroid_cmd(pattern="getmsg( ?(.*)|$)")
async def get_restricted_msg(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        await event.eor("`Пожалуйста, укажите ссылку!`", time=5)
        return
    
    xx = await event.eor("`Загрузка...`")
    chat, msg = get_chat_and_msgid(match)
    if not (chat and msg):
        return await event.eor(
            "Неверная ссылка!\nПримеры:\n"
            "`https://t.me/TeamUltroid/3`\n"
            "`https://t.me/c/1313492028/3`\n"
            "`tg://openmessage?user_id=1234567890&message_id=1`"
        )
    
    try:
        input_entity = await event.client.get_input_entity(chat)
        message = await event.client.get_messages(input_entity, ids=msg)
    except BaseException as er:
        return await event.eor(f"**ОШИБКА**\n`{er}`")
    
    if not message:
        return await event.eor("`Сообщение не найдено или не существует.`")
    
    try:
        await event.client.send_message(event.chat_id, message)
        await xx.try_delete()
        return
    except ChatForwardsRestrictedError:
        pass
    
    if message.media:
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            media_path, _ = await event.client.fast_downloader(message.document, show_progress=True, event=xx, message=get_string("com_5"))

            caption = message.text or ""

            attributes = []
            if message.video:
                duration = await get_video_duration(media_path.name)
                
                width, height = 0, 0
                for attribute in message.document.attributes:
                    if isinstance(attribute, DocumentAttributeVideo):
                        width = attribute.w
                        height = attribute.h
                        break
                
                thumb_path = media_path.name + "_thumb.jpg"
                await get_thumbnail(media_path.name, thumb_path)

                attributes.append(
                    DocumentAttributeVideo(
                        duration=int(duration) if duration else 0,
                        w=width,
                        h=height,
                        supports_streaming=True,
                    )
                )
            await xx.edit(get_string("com_6"))
            media_path, _ = await event.client.fast_uploader(media_path.name, event=xx, show_progress=True, to_delete=True)

            try:
                await event.client.send_file(
                    event.chat_id,
                    media_path,
                    caption=caption,
                    force_document=False,
                    supports_streaming=True if message.video else False,
                    thumb=thumb_path if message.video else None,
                    attributes=attributes if message.video else None,
                )
            except MessageTooLongError:
                if len(caption) > CAPTION_LIMIT:
                    caption = caption[:CAPTION_LIMIT] + "..."
                await event.client.send_file(
                    event.chat_id,
                    media_path,
                    caption=caption,
                    force_document=False,  # Установите True, если хотите отправить как документ
                    supports_streaming=True if message.video else False,
                    thumb=thumb_path if message.video else None,
                    attributes=attributes if message.video else None,
                )

            if message.video and os.path.exists(thumb_path):
                os.remove(thumb_path)
            await xx.try_delete()
        else:
            await event.eor("`Не удалось обработать этот тип медиа.`")
    else:
        await event.eor("`В сообщении нет медиа.`")