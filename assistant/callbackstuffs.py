import ast
import asyncio
import re
import sys
import time
from asyncio.exceptions import TimeoutError as AsyncTimeOut
from os import execl, remove
from random import choice

from bs4 import BeautifulSoup as bs

try:
    from pyUltroid.fns.gDrive import GDriveManager
except ImportError:
    GDriveManager = None
from telethon import Button, events
from catbox import CatboxUploader
from telethon.tl.types import MessageMediaWebPage
from telethon.utils import get_peer_id

from pyUltroid.fns.helper import fast_download, progress
from pyUltroid.fns.tools import Carbon, async_searcher, get_paste, telegraph_client
from pyUltroid.startup.loader import Loader

from . import *

# --------------------------------------------------------------------#
telegraph = telegraph_client()
GDrive = GDriveManager() if GDriveManager else None
uploader = CatboxUploader()
# --------------------------------------------------------------------#

def text_to_url(event):
    """функция для получения URL медиа (с|без) веб-страницы"""
    if isinstance(event.media, MessageMediaWebPage):
        webpage = event.media.webpage
        if not isinstance(webpage, types.WebPageEmpty) and webpage.type in ["photo"]:
            return webpage.display_url
    return event.text


# --------------------------------------------------------------------#

_buttons = {
    "otvars": {
        "text": "Другие переменные для настройки для @TeamTeleFriend:",
        "buttons": [
            [
                Button.inline("Tᴀɢ Lᴏɢɢᴇʀ", data="taglog"),
                Button.inline("SᴜᴘᴇʀFʙᴀɴ", data="cbs_sfban"),
            ],
            [
                Button.inline("Sudo Mode", data="sudo"),
                Button.inline("Handler", data="hhndlr"),
            ],
            [
                Button.inline("Extra Plugins", data="plg"),
                Button.inline("Addons", data="eaddon"),
            ],
            [
                Button.inline("Emoji in Help", data="emoj"),
                Button.inline("Set gDrive", data="gdrive"),
            ],
            [
                Button.inline("Inline Pic", data="inli_pic"),
                Button.inline("Sudo HNDLR", data="shndlr"),
            ],
            [Button.inline("Dual Mode", "cbs_oofdm")],
            [Button.inline("« Назад", data="setter")],
        ],
    },
    "sfban": {
        "text": "Настройки SuperFban:",
        "buttons": [
            [Button.inline("FBᴀɴ Gʀᴏᴜᴘ", data="sfgrp")],
            [Button.inline("Exᴄʟᴜᴅᴇ Fᴇᴅs", data="abs_sfexf")],
            [Button.inline("« Назад", data="cbs_otvars")],
        ],
    },
    "apauto": {
        "text": "Это автоматически одобрит на исходящие сообщения",
        "buttons": [
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ ON", data="apon")],
            [Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ OFF", data="apof")],
            [Button.inline("« Назад", data="cbs_pmcstm")],
        ],
    },
    "alvcstm": {
        "text": f"Настройте ваш {HNDLR}alive. Выберите из вариантов ниже -",
        "buttons": [
            [Button.inline("Aʟɪᴠᴇ Tᴇxᴛ", data="abs_alvtx")],
            [Button.inline("Aʟɪᴠᴇ ᴍᴇᴅɪᴀ", data="alvmed")],
            [Button.inline("Dᴇʟᴇᴛᴇ Aʟɪᴠᴇ Mᴇᴅɪᴀ", data="delmed")],
            [Button.inline("« Назад", data="setter")],
        ],
    },
    "pmcstm": {
        "text": "Настройте ваши параметры PMPERMIT -",
        "buttons": [
            [
                Button.inline("Pᴍ Tᴇxᴛ", data="pmtxt"),
                Button.inline("Pᴍ Mᴇᴅɪᴀ", data="pmmed"),
            ],
            [
                Button.inline("Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ", data="cbs_apauto"),
                Button.inline("PMLOGGER", data="pml"),
            ],
            [
                Button.inline("Sᴇᴛ Wᴀʀɴs", data="swarn"),
                Button.inline("Dᴇʟᴇᴛᴇ Pᴍ Mᴇᴅɪᴀ", data="delpmmed"),
            ],
            [Button.inline("PMPermit Type", data="cbs_pmtype")],
            [Button.inline("« Назад", data="cbs_ppmset")],
        ],
    },
    "pmtype": {
        "text": "Выберите тип PMPermit, который нужен.",
        "buttons": [
            [Button.inline("Inline", data="inpm_in")],
            [Button.inline("Normal", data="inpm_no")],
            [Button.inline("« Назад", data="cbs_pmcstm")],
        ],
    },
    "ppmset": {
        "text": "Настройки PMPermit:",
        "buttons": [
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oɴ", data="pmon")],
            [Button.inline("Tᴜʀɴ PMPᴇʀᴍɪᴛ Oғғ", data="pmoff")],
            [Button.inline("Cᴜsᴛᴏᴍɪᴢᴇ PMPᴇʀᴍɪᴛ", data="cbs_pmcstm")],
            [Button.inline("« Назад", data="setter")],
        ],
    },
    "chatbot": {
        "text": "С помощью этой функции вы можете общаться с людьми через вашего бота-ассистента.\n[Подробнее](https://t.me/TeleFriendUpdates/2)",
        "buttons": [
            [
                Button.inline("Cʜᴀᴛ Bᴏᴛ  Oɴ", data="onchbot"),
                Button.inline("Cʜᴀᴛ Bᴏᴛ  Oғғ", data="ofchbot"),
            ],
            [
                Button.inline("Bᴏᴛ Wᴇʟᴄᴏᴍᴇ", data="bwel"),
                Button.inline("Bᴏᴛ Wᴇʟᴄᴏᴍᴇ Mᴇᴅɪᴀ", data="botmew"),
            ],
            [Button.inline("Bᴏᴛ Iɴғᴏ Tᴇxᴛ", data="botinfe")],
            [Button.inline("Fᴏʀᴄᴇ Sᴜʙsᴄʀɪʙᴇ", data="pmfs")],
            [Button.inline("« Назад", data="setter")],
        ],
    },
    "vcb": {
        "text": "С помощью этой функции вы можете воспроизводить песни в групповом голосовом чате\n\n[подробнее](https://t.me/TeleFriendUpdates/4)",
        "buttons": [
            [Button.inline("VC Sᴇssɪᴏɴ", data="abs_vcs")],
            [Button.inline("« Назад", data="setter")],
        ],
    },
    "oofdm": {
        "text": "О [Dual Mode](https://t.me/TeleFriendUpdates/18)",
        "buttons": [
            [
                Button.inline("Dᴜᴀʟ Mᴏᴅᴇ Oɴ", "dmof"),
                Button.inline("Dᴜᴀʟ Mᴏᴅᴇ Oғғ", "dmof"),
            ],
            [Button.inline("Dᴜᴀʟ Mᴏᴅᴇ Hɴᴅʟʀ", "dmhn")],
            [Button.inline("« Back", data="cbs_otvars")],
        ],
    },
    "apiset": {
        "text": get_string("ast_1"),
        "buttons": [
            [Button.inline("Remove.bg API", data="abs_rmbg")],
            [Button.inline("DEEP API", data="abs_dapi")],
            [Button.inline("OCR API", data="abs_oapi")],
            [Button.inline("« Back", data="setter")],
        ],
    },
}

_convo = {
    "rmbg": {
        "var": "RMBG_API",
        "name": "Remove.bg API Key",
        "text": get_string("ast_2"),
        "back": "cbs_apiset",
    },
    "dapi": {
        "var": "DEEP_AI",
        "name": "Deep AI Api Key",
        "text": "Получите ваш Deep API с deepai.org и отправьте сюда.",
        "back": "cbs_apiset",
    },
    "oapi": {
        "var": "OCR_API",
        "name": "Ocr Api Key",
        "text": "Получите ваш OCR API с ocr.space и отправьте сюда.",
        "back": "cbs_apiset",
    },
    "pmlgg": {
        "var": "PMLOGGROUP",
        "name": "Pm Log Group",
        "text": "Отправьте ID чата, который вы хотите сохранить как группу для логов ЛС.",
        "back": "pml",
    },
    "vcs": {
        "var": "VC_SESSION",
        "name": "Vc Session",
        "text": "**VC сессия**\nВведите новую сессию, которую вы создали для VC бота.\n\nИспользуйте /cancel для отмены операции.",
        "back": "cbs_vcb",
    },
    "settag": {
        "var": "TAG_LOG",
        "name": "Tag Log Group",
        "text": f"Создайте группу, добавьте вашего ассистента и сделайте его администратором.\nПолучите `{HNDLR}id` этой группы и отправьте сюда для тегов логов.\n\nИспользуйте /cancel для отмены.",
        "back": "taglog",
    },
    "alvtx": {
        "var": "ALIVE_TEXT",
        "name": "Alive Text",
        "text": "**Alive Text**\nВведите новый текст alive.\n\nИспользуйте /cancel для отмены операции.",
        "back": "cbs_alvcstm",
    },
    "sfexf": {
        "var": "EXCLUDE_FED",
        "name": "Excluded Fed",
        "text": "Отправьте ID федераций, которые вы хотите исключить из бана. Разделяйте пробелом.\nнапример`id1 id2 id3`\nУстановите `None`, если не хотите исключать.\nИспользуйте /cancel для возврата.",
        "back": "cbs_sfban",
    },
}


TOKEN_FILE = "resources/auths/auth_token.txt"


@callback(
    re.compile(
        "sndplug_(.*)",
    ),
    owner=True,
)
async def send(eve):
    key, name = (eve.data_match.group(1)).decode("UTF-8").split("_")
    thumb = "resources/extras/inline.jpg"
    await eve.answer("■ Отправка ■")
    data = f"uh_{key}_"
    index = None
    if "|" in name:
        name, index = name.split("|")
    key = "plugins" if key == "Official" else key.lower()
    plugin = f"{key}/{name}.py"
    _ = f"pasta-{plugin}"
    if index is not None:
        data += f"|{index}"
        _ += f"|{index}"
    buttons = [
        [
            Button.inline(
                "« Pᴀsᴛᴇ »",
                data=_,
            )
        ],
        [
            Button.inline("« Назад", data=data),
        ],
    ]
    try:
        await eve.edit(file=plugin, thumb=thumb, buttons=buttons)
    except Exception as er:
        await eve.answer(str(er), alert=True)


heroku_api, app_name = Var.HEROKU_API, Var.HEROKU_APP_NAME


@callback("updatenow", owner=True)
async def update(eve):
    repo = Repo()
    ac_br = repo.active_branch
    ups_rem = repo.remote("upstream")
    if heroku_api:
        import heroku3

        try:
            heroku = heroku3.from_key(heroku_api)
            heroku_app = None
            heroku_applications = heroku.apps()
        except BaseException as er:
            LOGS.exception(er)
            return await eve.edit("`Неверный HEROKU_API.`")
        for app in heroku_applications:
            if app.name == app_name:
                heroku_app = app
        if not heroku_app:
            await eve.edit("`Неверный HEROKU_APP_NAME.`")
            repo.__del__()
            return
        await eve.edit(get_string("clst_1"))
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", f"https://api:{heroku_api}@"
        )

        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec=f"HEAD:refs/heads/{ac_br}", force=True)
        except GitCommandError as error:
            await eve.edit(f"`Вот лог ошибки:\n{error}`")
            repo.__del__()
            return
        await eve.edit("`Успешно обновлено!\nПерезапуск, пожалуйста, подождите...`")
    else:
        await eve.edit(get_string("clst_1"))
        call_back()
        await bash("git pull && pip3 install -r requirements.txt")
        await bash("pip3 install -r requirements.txt --break-system-packages")
        execl(sys.executable, sys.executable, "-m", "pyUltroid")

@callback(re.compile("changes(.*)"), owner=True)
async def changes(okk):
    match = okk.data_match.group(1).decode("utf-8")
    await okk.answer(get_string("clst_3"))
    repo = Repo.init()
    button = [[Button.inline("Обновить сейчас", data="updatenow")]]
    changelog, tl_chnglog = await gen_chlog(
        repo, f"HEAD..upstream/{repo.active_branch}"
    )
    cli = "\n\nНажмите кнопку ниже для обновления!"
    if not match:
        try:
            if len(tl_chnglog) > 700:
                tl_chnglog = f"{tl_chnglog[:700]}..."
                button.append([Button.inline("Показать полностью", "changesall")])
            await okk.edit("• Запись изменений 📝 •")
            img = await Carbon(
                file_name="changelog",
                code=tl_chnglog,
                backgroundColor=choice(ATRA_COL),
                language="md",
            )
            return await okk.edit(
                f"**• TeleFriend Userbot •**{cli}", file=img, buttons=button
            )
        except Exception as er:
            LOGS.exception(er)
    changelog_str = changelog + cli
    if len(changelog_str) > 1024:
        await okk.edit(get_string("upd_4"))
        await asyncio.sleep(2)
        with open("ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await okk.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=button,
        )
        remove("ultroid_updates.txt")
        return
    await okk.edit(
        changelog_str,
        buttons=button,
        parse_mode="html",
    )


@callback(
    re.compile(
        "pasta-(.*)",
    ),
    owner=True,
)
async def _(e):
    ok = (e.data_match.group(1)).decode("UTF-8")
    index = None
    if "|" in ok:
        ok, index = ok.split("|")
    with open(ok, "r") as hmm:
        _, data = await get_paste(hmm.read())
    if not data.get("link"):
        return await e.answer(key[:30], alert=True)
    if not key.startswith("http"):
        link, raw = data["link"], data["raw"]
    else:
        link = key
        raw = f"{key}/raw"
    if ok.startswith("addons"):
        key = "Addons"
    elif ok.startswith("vcbot"):
        key = "VCBot"
    else:
        key = "Official"
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
    await e.edit(
        "",
        buttons=[
            [Button.url("Lɪɴᴋ", link), Button.url("Rᴀᴡ", raw)],
            [Button.inline("« Назад", data=data)],
        ],
    )


@callback(re.compile("cbs_(.*)"), owner=True)
async def _edit_to(event):
    match = event.data_match.group(1).decode("utf-8")
    data = _buttons.get(match)
    if not data:
        return
    await event.edit(data["text"], buttons=data["buttons"], link_preview=False)


@callback(re.compile("abs_(.*)"), owner=True)
async def convo_handler(event: events.CallbackQuery):
    match = event.data_match.group(1).decode("utf-8")
    if not _convo.get(match):
        return
    await event.delete()
    get_ = _convo[match]
    back = get_["back"]
    async with event.client.conversation(event.sender_id) as conv:
        await conv.send_message(get_["text"])
        response = await conv.get_response()
        themssg = response.message
        try:
            themssg = ast.literal_eval(themssg)
        except Exception:
            pass
        if themssg == "/cancel":
            return await conv.send_message(
                "Отменено!!",
                buttons=get_back_button(back),
            )
        await setit(event, get_["var"], themssg)
        await conv.send_message(
            f"{get_['name']} изменён на `{themssg}`",
            buttons=get_back_button(back),
        )


@callback("authorise", owner=True)
async def _(e):
    if not e.is_private:
        return
    url = GDrive._create_token_file()
    await e.edit("Перейдите по ссылке ниже и отправьте код!")
    async with asst.conversation(e.sender_id) as conv:
        await conv.send_message(url)
        code = await conv.get_response()
        if GDrive._create_token_file(code=code.text):
            await conv.send_message(
                "`Успешно!\nВы готовы использовать Google Drive с TeleFriend Userbot.`",
                buttons=Button.inline("Главное меню", data="setter"),
            )
        else:
            await conv.send_message("Неверный код! Нажмите авторизоваться снова.")


@callback("folderid", owner=True, func=lambda x: x.is_private)
async def _(e):
    if not e.is_private:
        return
    msg = (
        "Отправьте ID папки\n\n"
        + "Для ID папки:\n"
        + "1. Откройте приложение Google Drive.\n"
        + "2. Создайте папку.\n"
        + "3. Сделайте эту папку публичной.\n"
        + "4. Отправьте ссылку на эту папку."
    )
    await e.delete()
    async with asst.conversation(e.sender_id, timeout=150) as conv:
        await conv.send_message(msg)
        repl = await conv.get_response()
        id = repl.text
        if id.startswith("https"):
            id = id.split("?id=")[-1]
        udB.set_key("GDRIVE_FOLDER_ID", id)
        await repl.reply(
            "`Успешно.`",
            buttons=get_back_button("gdrive"),
        )


@callback("gdrive", owner=True)
async def _(e):
    if not e.is_private:
        return
    await e.edit(
        "Нажмите Авторизоваться и отправьте код.\n\nВы можете использовать свой собственный CLIENT ID и SECRET по [этой](https://t.me/TeleFriendUpdates/37) ссылке",
        buttons=[
            [
                Button.inline("ID папки", data="folderid"),
                Button.inline("Авторизоваться", data="authorise"),
            ],
            [Button.inline("« Назад", data="cbs_otvars")],
        ],
        link_preview=False,
    )


@callback("dmof", owner=True)
async def rhwhe(e):
    if udB.get_key("DUAL_MODE"):
        udB.del_key("DUAL_MODE")
        key = "Off"
    else:
        udB.set_key("DUAL_MODE", "True")
        key = "On"
    Msg = f"Dual Mode : {key}"
    await e.edit(Msg, buttons=get_back_button("cbs_otvars"))


@callback("dmhn", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "DUAL_HNDLR"
    name = "Dual Handler"
    CH = udB.get_key(var) or "/"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Отправьте символ, который вы хотите использовать как Handler/Trigger для вашего бота-ассистента\nВаш текущий Handler [ `{CH}` ]\n\n используйте /cancel для отмены.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Неверный Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} изменён на {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("emoj", owner=True)
async def emoji(event):
    await event.delete()
    pru = event.sender_id
    var = "EMOJI_IN_HELP"
    name = f"Emoji в меню `{HNDLR}help`"
    async with event.client.conversation(pru) as conv:
        await conv.send_message("Отправьте эмодзи, которое хотите установить 🙃.\n\nИспользуйте /cancel для отмены.")
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Неверный эмодзи",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} изменён на {themssg}\n",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("plg", owner=True)
async def pluginch(event):
    await event.delete()
    pru = event.sender_id
    var = "PLUGIN_CHANNEL"
    name = "Канал плагинов"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Отправьте ID или имя пользователя канала, откуда вы хотите установить все плагины\n\nНаш канал~ @ultroidplugins\n\nИспользуйте /cancel для отмены.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", HNDLR)):
            await conv.send_message(
                "Неверный канал",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} изменён на {themssg}\n После настройки всех параметров выполните перезапуск",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("hhndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "HNDLR"
    name = "Handler/ Trigger"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            f"Отправьте символ, который вы хотите использовать как Handler/Trigger для бота\nВаш текущий Handler [ `{HNDLR}` ]\n\n используйте /cancel для отмены.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Неверный Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "Это не может использоваться как handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} изменён на {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("shndlr", owner=True)
async def hndlrr(event):
    await event.delete()
    pru = event.sender_id
    var = "SUDO_HNDLR"
    name = "Sudo Handler"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "Отправьте символ, который вы хотите использовать как Sudo Handler/Trigger для бота\n\n используйте /cancel для отмены."
        )

        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_otvars"),
            )
        elif len(themssg) > 1:
            await conv.send_message(
                "Неверный Handler",
                buttons=get_back_button("cbs_otvars"),
            )
        elif themssg.startswith(("/", "#", "@")):
            await conv.send_message(
                "Это не может использоваться как handler",
                buttons=get_back_button("cbs_otvars"),
            )
        else:
            await setit(event, var, themssg)
            await conv.send_message(
                f"{name} изменён на {themssg}",
                buttons=get_back_button("cbs_otvars"),
            )


@callback("taglog", owner=True)
async def tagloggrr(e):
    BUTTON = [
        [Button.inline("SET TAG LOG", data="abs_settag")],
        [Button.inline("DELETE TAG LOG", data="deltag")],
        get_back_button("cbs_otvars"),
    ]
    await e.edit(
        "Выберите опции",
        buttons=BUTTON,
    )


@callback("deltag", owner=True)
async def _(e):
    udB.del_key("TAG_LOG")
    await e.answer("Готово!!! Tag Logger был выключен")


@callback("eaddon", owner=True)
async def pmset(event):
    BT = (
        [Button.inline("Aᴅᴅᴏɴs  Oғғ", data="edof")]
        if udB.get_key("ADDONS")
        else [Button.inline("Aᴅᴅᴏɴs  Oɴ", data="edon")]
    )

    await event.edit(
        "ADDONS~ Дополнительные плагины:",
        buttons=[
            BT,
            [Button.inline("« Назад", data="cbs_otvars")],
        ],
    )


@callback("edon", owner=True)
async def eddon(event):
    var = "ADDONS"
    await setit(event, var, "True")
    await event.edit(
        "Готово! ADDONS был включен!!\n\n После настройки всех параметров выполните перезапуск",
        buttons=get_back_button("eaddon"),
    )


@callback("edof", owner=True)
async def eddof(event):
    udB.set_key("ADDONS", "False")
    await event.edit(
        "Готово! ADDONS был выключен!! После настройки всех параметров выполните перезапуск",
        buttons=get_back_button("eaddon"),
    )


@callback("sudo", owner=True)
async def pmset(event):
    BT = (
        [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oғғ", data="ofsudo")]
        if udB.get_key("SUDO")
        else [Button.inline("Sᴜᴅᴏ Mᴏᴅᴇ  Oɴ", data="onsudo")]
    )

    await event.edit(
        f"SUDO MODE ~ Некоторые люди могут использовать вашего бота, которых вы выбрали. Чтобы узнать больше, используйте `{HNDLR}help sudo`",
        buttons=[
            BT,
            [Button.inline("« Назад", data="cbs_otvars")],
        ],
    )


@callback("onsudo", owner=True)
async def eddon(event):
    var = "SUDO"
    await setit(event, var, "True")
    await event.edit(
        "Готово! SUDO MODE был включен!!\n\n После настройки всех параметров выполните перезапуск",
        buttons=get_back_button("sudo"),
    )


@callback("ofsudo", owner=True)
async def eddof(event):
    var = "SUDO"
    await setit(event, var, "False")
    await event.edit(
        "Готово! SUDO MODE был выключен!! После настройки всех параметров выполните перезапуск",
        buttons=get_back_button("sudo"),
    )


@callback("sfgrp", owner=True)
async def sfgrp(event):
    await event.delete()
    name = "FBan Group ID"
    var = "FBAN_GROUP_ID"
    pru = event.sender_id
    async with asst.conversation(pru) as conv:
        await conv.send_message(
            f"Создайте группу, добавьте @MissRose_Bot, отправьте `{HNDLR}id`, скопируйте и отправьте сюда.\nИспользуйте /cancel для возврата.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_sfban"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} изменён на {themssg}",
            buttons=get_back_button("cbs_sfban"),
        )


@callback("alvmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "ALIVE_PIC"
    name = "Alive Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Alive Media**\nОтправьте мне фото/gif/медиа для установки в качестве alive медиа.\n\nИспользуйте /cancel для отмены операции.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Операция отменена!!",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        except BaseException as er:
            LOGS.exception(er)
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            media = await event.client.download_media(response, "alvpc")
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Прервано.",
                    buttons=get_back_button("cbs_alvcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} был установлен.",
            buttons=get_back_button("cbs_alvcstm"),
        )


@callback("delmed", owner=True)
async def dell(event):
    try:
        udB.del_key("ALIVE_PIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_alabs_vcstm")
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=get_back_button("cbs_alabs_vcstm"),
        )


@callback("inpm_in", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "True")
    await event.edit(
        "Готово!! Тип PMPermit установлен на встроенный!",
        buttons=[[Button.inline("« Назад", data="cbs_pmtype")]],
    )


@callback("inpm_no", owner=True)
async def inl_on(event):
    var = "INLINE_PM"
    await setit(event, var, "False")
    await event.edit(
        "Готово!! Тип PMPermit установлен на обычный!",
        buttons=[[Button.inline("« Назад", data="cbs_pmtype")]],
    )


@callback("pmtxt", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "PM_TEXT"
    name = "PM Text"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Text**\nВведите новый текст pmpermit.\n\nВы можете использовать `{name}` `{fullname}` `{count}` `{mention}` `{username}` для получения этих данных от пользователя тоже\n\nИспользуйте /cancel для отмены операции.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        if len(themssg) > 4090:
            return await conv.send_message(
                "Сообщение слишком длинное!\nПожалуйста, дайте более короткое сообщение!!",
                buttons=get_back_button("cbs_pmcstm"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} изменён на {themssg}\n\nПосле настройки всех параметров выполните перезапуск",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("swarn", owner=True)
async def name(event):
    m = range(1, 10)
    tultd = [Button.inline(f"{x}", data=f"wrns_{x}") for x in m]
    lst = list(zip(tultd[::3], tultd[1::3], tultd[2::3]))
    lst.append([Button.inline("« Назад", data="cbs_pmcstm")])
    await event.edit(
        "Выберите количество предупреждений для пользователя перед блокировкой в ЛС.",
        buttons=lst,
    )


@callback(re.compile(b"wrns_(.*)"), owner=True)
async def set_wrns(event):
    value = int(event.data_match.group(1).decode("UTF-8"))
    if dn := udB.set_key("PMWARNS", value):
        await event.edit(
            f"Предупреждения ЛС установлены на {value}.\nНовые пользователи будут иметь {value} шансов в ЛС перед баном.",
            buttons=get_back_button("cbs_pmcstm"),
        )
    else:
        await event.edit(
            f"Что-то пошло не так, проверьте ваши `{HNDLR}logs`!",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("pmmed", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "PMPIC"
    name = "PM Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**PM Media**\nОтправьте мне фото/gif/стикер/ссылку для установки в качестве медиа pmpermit.\n\nИспользуйте /cancel для отмены операции.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Операция отменена!!",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "pmpc")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        elif response.sticker:
            url = response.file.id
        else:
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Прервано.",
                    buttons=get_back_button("cbs_pmcstm"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} был установлен.",
            buttons=get_back_button("cbs_pmcstm"),
        )


@callback("delpmmed", owner=True)
async def dell(event):
    try:
        udB.del_key("PMPIC")
        return await event.edit(
            get_string("clst_5"), buttons=get_back_button("cbs_pmcstm")
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Настройки", data="setter")]],
        )


@callback("apon", owner=True)
async def apon(event):
    var = "AUTOAPPROVE"
    await setit(event, var, "True")
    await event.edit(
        "Готово!! AUTOAPPROVE Запущен!!",
        buttons=[[Button.inline("« Назад", data="cbs_apauto")]],
    )


@callback("apof", owner=True)
async def apof(event):
    try:
        udB.set_key("AUTOAPPROVE", "False")
        return await event.edit(
            "Готово! AUTOAPPROVE Остановлен!!",
            buttons=[[Button.inline("« Назад", data="cbs_apauto")]],
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Настройки", data="setter")]],
        )


@callback("pml", owner=True)
async def l_vcs(event):
    BT = (
        [Button.inline("PMLOGGER OFF", data="pmlogof")]
        if udB.get_key("PMLOG")
        else [Button.inline("PMLOGGER ON", data="pmlog")]
    )

    await event.edit(
        "PMLOGGER Это будет пересылать ваши ЛС в вашу приватную группу -",
        buttons=[
            BT,
            [Button.inline("PᴍLᴏɢɢᴇʀ Gʀᴏᴜᴘ", "abs_pmlgg")],
            [Button.inline("« Назад", data="cbs_pmcstm")],
        ],
    )


@callback("pmlog", owner=True)
async def pmlog(event):
    await setit(event, "PMLOG", "True")
    await event.edit(
        "Готово!! PMLOGGER Запущен!!",
        buttons=[[Button.inline("« Назад", data="pml")]],
    )


@callback("pmlogof", owner=True)
async def pmlogof(event):
    try:
        udB.del_key("PMLOG")
        return await event.edit(
            "Готово! PMLOGGER Остановлен!!",
            buttons=[[Button.inline("« Назад", data="pml")]],
        )
    except BaseException as er:
        LOGS.exception(er)
        return await event.edit(
            get_string("clst_4"),
            buttons=[[Button.inline("« Настройки", data="setter")]],
        )


@callback("pmon", owner=True)
async def pmonn(event):
    var = "PMSETTING"
    await setit(event, var, "True")
    await event.edit(
        "Готово! PMPermit был включен!!",
        buttons=[[Button.inline("« Назад", data="cbs_ppmset")]],
    )


@callback("pmoff", owner=True)
async def pmofff(event):
    var = "PMSETTING"
    await setit(event, var, "False")
    await event.edit(
        "Готово! PMPermit был выключен!!",
        buttons=[[Button.inline("« Назад", data="cbs_ppmset")]],
    )


@callback("botmew", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message("Отправьте любое медиа для сохранения в приветствии вашего бота ")
        msg = await conv.get_response()
        if not msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Прервано!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("STARTMEDIA", msg.file.id)
        await conv.send_message("Готово!", buttons=get_back_button("cbs_chatbot"))


@callback("botinfe", owner=True)
async def hhh(e):
    async with e.client.conversation(e.chat_id) as conv:
        await conv.send_message(
            "Отправьте сообщение для отображения, когда пользователь нажимает кнопку Info в приветствии бота!\n\nотправьте `False`, чтобы полностью удалить эту кнопку.."
        )
        msg = await conv.get_response()
        if msg.media or msg.text.startswith("/"):
            return await conv.send_message(
                "Прервано!", buttons=get_back_button("cbs_chatbot")
            )
        udB.set_key("BOT_INFO_START", msg.text)
        await conv.send_message("Готово!", buttons=get_back_button("cbs_chatbot"))


@callback("pmfs", owner=True)
async def heheh(event):
    Ll = []
    err = ""
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message(
            "• Отправьте ID чата(ов), которые вы хотите, чтобы пользователь присоединился перед использованием Chat/Pm Bot\n\n• Отправьте /clear для отключения PmBot Force sub..\n• • Отправьте /cancel для остановки этого процесса.."
        )
        await conv.send_message(
            "Пример : \n`-1001234567\n-100778888`\n\nДля нескольких чатов."
        )
        try:
            msg = await conv.get_response()
        except AsyncTimeOut:
            return await conv.send_message("**• Время вышло!**\nНачните с /start.")
        if not msg.text or msg.text.startswith("/"):
            timyork = "Отменено!"
            if msg.text == "/clear":
                udB.del_key("PMBOT_FSUB")
                timyork = "Готово! Принудительная подписка остановлена\nПерезапустите вашего бота!"
            return await conv.send_message(
                "Отменено!", buttons=get_back_button("cbs_chatbot")
            )
        for chat in msg.message.split("\n"):
            if chat.startswith("-") or chat.isdigit():
                chat = int(chat)
            try:
                CHSJSHS = await event.client.get_entity(chat)
                Ll.append(get_peer_id(CHSJSHS))
            except Exception as er:
                err += f"**{chat}** : {er}\n"
        if err:
            return await conv.send_message(err)
        udB.set_key("PMBOT_FSUB", str(Ll))
        await conv.send_message(
            "Готово!\nПерезапустите вашего бота.", buttons=get_back_button("cbs_chatbot")
        )


@callback("bwel", owner=True)
async def name(event):
    await event.delete()
    pru = event.sender_id
    var = "STARTMSG"
    name = "Bot Welcome Message:"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**BOT WELCOME MSG**\nВведите сообщение, которое вы хотите показывать, когда кто-то запускает вашего бота-ассистента.\nВы можете использовать `{me}` , `{mention}` Параметры тоже\nИспользуйте /cancel для отмены операции.",
        )
        response = conv.wait_event(events.NewMessage(chats=pru))
        response = await response
        themssg = response.message.message
        if themssg == "/cancel":
            return await conv.send_message(
                "Отменено!!",
                buttons=get_back_button("cbs_chatbot"),
            )
        await setit(event, var, themssg)
        await conv.send_message(
            f"{name} изменён на {themssg}",
            buttons=get_back_button("cbs_chatbot"),
        )


@callback("onchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "True")
    Loader(path="assistant/pmbot.py", key="PM Bot").load()
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.add_event_handler(i, events.NewMessage(**e))
    await event.edit(
        "Готово! Теперь вы можете общаться с людьми через этого бота",
        buttons=[Button.inline("« Назад", data="cbs_chatbot")],
    )


@callback("ofchbot", owner=True)
async def chon(event):
    var = "PMBOT"
    await setit(event, var, "False")
    if AST_PLUGINS.get("pmbot"):
        for i, e in AST_PLUGINS["pmbot"]:
            event.client.remove_event_handler(i)
    await event.edit(
        "Готово! Общение с людьми через этого бота остановлено.",
        buttons=[Button.inline("« Назад", data="cbs_chatbot")],
    )


@callback("inli_pic", owner=True)
async def media(event):
    await event.delete()
    pru = event.sender_id
    var = "INLINE_PIC"
    name = "Inline Media"
    async with event.client.conversation(pru) as conv:
        await conv.send_message(
            "**Inline Media**\nОтправьте мне фото/gif/или ссылку для установки в качестве встроенного медиа.\n\nИспользуйте /cancel для отмены операции.",
        )
        response = await conv.get_response()
        try:
            themssg = response.message
            if themssg == "/cancel":
                return await conv.send_message(
                    "Операция отменена!!",
                    buttons=get_back_button("setter"),
                )
        except BaseException as er:
            LOGS.exception(er)
        media = await event.client.download_media(response, "inlpic")
        if (
            not (response.text).startswith("/")
            and response.text != ""
            and (not response.media or isinstance(response.media, MessageMediaWebPage))
        ):
            url = text_to_url(response)
        else:
            try:
                url = uploader.upload_file(media)
                remove(media)
            except BaseException as er:
                LOGS.exception(er)
                return await conv.send_message(
                    "Прервано.",
                    buttons=get_back_button("setter"),
                )
        await setit(event, var, url)
        await conv.send_message(
            f"{name} был установлен.",
            buttons=get_back_button("setter"),
        )


FD_MEDIA = {}


@callback(re.compile("fd(.*)"), owner=True)
async def fdroid_dler(event):
    uri = event.data_match.group(1).decode("utf-8")
    if FD_MEDIA.get(uri):
        return await event.edit(file=FD_MEDIA[uri])
    await event.answer("• Запуск загрузки •", alert=True)
    await event.edit("• Загрузка.. •")
    URL = f"https://f-droid.org/packages/{uri}"
    conte = await async_searcher(URL, re_content=True)
    BSC = bs(conte, "html.parser", from_encoding="utf-8")
    dl_ = BSC.find("p", "package-version-download").find("a")["href"]
    title = BSC.find("h3", "package-name").text.strip()
    thumb = BSC.find("img", "package-icon")["src"]
    if thumb.startswith("/"):
        thumb = f"https://f-droid.org{thumb}"
    thumb, _ = await fast_download(thumb, filename=f"{uri}.png")
    s_time = time.time()
    file, _ = await fast_download(
        dl_,
        filename=f"{title}.apk",
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(
                d,
                t,
                event,
                s_time,
                "Загрузка...",
            )
        ),
    )

    time.time()
    n_file = await event.client.fast_uploader(
        file, show_progress=True, event=event, message="Загрузка...", to_delete=True
    )
    buttons = Button.switch_inline("Поиск обратно", query="fdroid", same_peer=True)
    try:
        msg = await event.edit(
            f"**• [{title}]({URL}) •**", file=n_file, thumb=thumb, buttons=buttons
        )
    except Exception as er:
        LOGS.exception(er)
        try:
            msg = await event.client.edit_message(
                await event.get_input_chat(),
                event.message_id,
                f"**• [{title}]({URL}) •**",
                buttons=buttons,
                thumb=thumb,
                file=n_file,
            )
        except Exception as er:
            os.remove(thumb)
            LOGS.exception(er)
            return await event.edit(f"**ОШИБКА**: `{er}`", buttons=buttons)
    if msg and hasattr(msg, "media"):
        FD_MEDIA.update({uri: msg.media})
    os.remove(thumb)