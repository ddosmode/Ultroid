# TeleFriend - Пользовательский бот
# Copyright (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, прочтите GNU Affero General Public License в
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}addnote <word><reply to a message>`
    Добавить заметку в используемый чат с ответным сообщением и выбранным словом.

• `{i}remnote <word>`
    Удалить заметку из используемого чата.

• `{i}listnote`
    Список всех заметок.

• Использование :
    установите заметки в группе, чтобы все могли их использовать.
    введите `#(Ключевое слово заметки)`, чтобы получить её
"""
import os

from . import upload_file as uf
from telethon.utils import pack_bot_file_id

from pyUltroid.dB.notes_db import add_note, get_notes, list_note, rem_note
from pyUltroid.fns.tools import create_tl_btn, format_btn, get_msg_button

from . import events, get_string, mediainfo, udB, ultroid_bot, ultroid_cmd
from ._inline import something


@ultroid_cmd(pattern="addnote( (.*)|$)", admins_only=True)
async def an(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    wt = await e.get_reply_message()
    chat = e.chat_id
    if not (wt and wrd):
        return await e.eor(get_string("notes_1"), time=5)
    if "#" in wrd:
        wrd = wrd.replace("#", "")
    btn = format_btn(wt.buttons) if wt.buttons else None
    if wt and wt.media:
        wut = mediainfo(wt.media)
        if wut.startswith(("pic", "gif")):
            dl = await wt.download_media()
            m = uf(dl)
            os.remove(dl)
        elif wut == "video":
            if wt.media.document.size > 8 * 1000 * 1000:
                return await e.eor(get_string("com_4"), time=5)
            dl = await wt.download_media()
            m = uf(dl)
            os.remove(dl)
        else:
            m = pack_bot_file_id(wt.media)
        if wt.text:
            txt = wt.text
            if not btn:
                txt, btn = get_msg_button(wt.text)
            add_note(chat, wrd, txt, m, btn)
        else:
            add_note(chat, wrd, None, m, btn)
    else:
        txt = wt.text
        if not btn:
            txt, btn = get_msg_button(wt.text)
        add_note(chat, wrd, txt, None, btn)
    await e.eor(get_string("notes_2").format(wrd))
    ultroid_bot.add_handler(notes, events.NewMessage())


@ultroid_cmd(pattern="remnote( (.*)|$)", admins_only=True)
async def rn(e):
    wrd = (e.pattern_match.group(1).strip()).lower()
    chat = e.chat_id
    if not wrd:
        return await e.eor(get_string("notes_3"), time=5)
    if wrd.startswith("#"):
        wrd = wrd.replace("#", "")
    rem_note(int(chat), wrd)
    await e.eor(f"Готово: заметка `#{wrd}` удалена.")


@ultroid_cmd(pattern="listnote$", admins_only=True)
async def lsnote(e):
    if x := list_note(e.chat_id):
        sd = "Найденные заметки в этом чате\n\n"
        return await e.eor(sd + x)
    await e.eor(get_string("notes_5"))


async def notes(e):
    xx = [z.replace("#", "") for z in e.text.lower().split() if z.startswith("#")]
    for word in xx:
        if k := get_notes(e.chat_id, word):
            msg = k["msg"]
            media = k["media"]
            if k.get("button"):
                btn = create_tl_btn(k["button"])
                return await something(e, msg, media, btn)
            await e.client.send_message(
                e.chat_id, msg, file=media, reply_to=e.reply_to_msg_id or e.id
            )


if udB.get_key("NOTE"):
    ultroid_bot.add_handler(notes, events.NewMessage())
