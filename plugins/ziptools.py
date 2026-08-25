# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочитайте GNU Affero General Public License в
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды

• `{i}zip <ответ на файл>`
    заархивировать файл, на который ответили
    Чтобы установить пароль на архив: `{i}zip <пароль>` ответ на файл

• `{i}unzip <ответ на zip-файл>`
    разархивировать файл, на который ответили.

• `{i}azip <ответ на файл>`
    добавить файл в пакет для пакетной загрузки в архив

• `{i}dozip`
    загрузить пакетный архив с файлами, добавленными через `{i}azip`
    Чтобы установить пароль: `{i}dozip <пароль>`

"""
import os
import time

from . import (
    HNDLR,
    ULTConfig,
    asyncio,
    bash,
    downloader,
    get_all_files,
    get_string,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(pattern="zip( (.*)|$)")
async def zipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                reply.file.name, reply.media.document, xx, t, get_string("com_5")
            )
            file = image.name
        else:
            file = await event.download_media(reply)
    inp = file.replace(file.split(".")[-1], "zip")
    if event.pattern_match.group(1).strip():
        await bash(
            f"zip -r --password {event.pattern_match.group(1).strip()} {inp} {file}"
        )
    else:
        await bash(f"zip -r {inp} {file}")
    k = time.time()
    n_file, _ = await event.client.fast_uploader(
        inp, show_progress=True, event=event, message="Загрузка...", to_delete=True
    )
    await event.client.send_file(
        event.chat_id,
        n_file,
        force_document=True,
        thumb=ULTConfig.thumb,
        caption=f"`{n_file.name}`",
        reply_to=reply,
    )
    os.remove(inp)
    os.remove(file)
    await xx.delete()


@ultroid_cmd(pattern="unzip( (.*)|$)")
async def unzipp(event):
    reply = await event.get_reply_message()
    file = event.pattern_match.group(1).strip()
    t = time.time()
    if not ((reply and reply.media) or file):
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if not hasattr(reply.media, "document"):
            return await xx.edit(get_string("zip_3"))
        file = reply.media.document
        if not reply.file.name.endswith(("zip", "rar", "exe")):
            return await xx.edit(get_string("zip_3"))
        image = await downloader(
            reply.file.name, reply.media.document, xx, t, get_string("com_5")
        )
        file = image.name
    if os.path.isdir("unzip"):
        await bash("rm -rf unzip")
    os.mkdir("unzip")
    await bash(f"7z x {file} -aoa -ounzip")
    await asyncio.sleep(4)
    ok = get_all_files("unzip")
    for x in ok:
        k = time.time()
        n_file, _ = await event.client.fast_uploader(
            x, show_progress=True, event=event, message="Загрузка...", to_delete=True
        )
        await event.client.send_file(
            event.chat_id,
            n_file,
            force_document=True,
            thumb=ULTConfig.thumb,
            caption=f"`{n_file.name}`",
        )
    await xx.delete()


@ultroid_cmd(pattern="addzip$")
async def azipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not (reply and reply.media):
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if not os.path.isdir("zip"):
        os.mkdir("zip")
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                f"zip/{reply.file.name}",
                reply.media.document,
                xx,
                t,
                get_string("com_5"),
            )

            file = image.name
        else:
            file = await event.download_media(reply.media, "zip/")
    await xx.edit(
        f"Файл `{file}` успешно загружен\nТеперь ответьте на другие файлы, чтобы добавить и заархивировать всё сразу"
    )


@ultroid_cmd(pattern="dozip( (.*)|$)")
async def do_zip(event):
    if not os.path.isdir("zip"):
        return await event.eor(get_string("zip_2").format(HNDLR))
    xx = await event.eor(get_string("com_1"))
    if event.pattern_match.group(1).strip():
        await bash(
            f"zip -r --password {event.pattern_match.group(1).strip()} ultroid.zip zip/*"
        )
    else:
        await bash("zip -r ultroid.zip zip/*")
    k = time.time()
    xxx = await uploader("ultroid.zip", "ultroid.zip", k, xx, get_string("com_6"))
    await event.client.send_file(
        event.chat_id,
        xxx,
        force_document=True,
        thumb=ULTConfig.thumb,
    )
    await bash("rm -rf zip")
    os.remove("ultroid.zip")
    await xx.delete()
