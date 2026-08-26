"""
✘ Доступные команды -

• `{i}webupload`
    Загрузить файлы на другой сервер.
"""

import os

from pyUltroid.fns.tools import _webupload_cache

from . import Button, asst, get_string, ultroid_cmd


@ultroid_cmd(pattern="webupload( (.*)|$)")
async def _(event):
    xx = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1).strip()
    if event.chat_id not in _webupload_cache:
        _webupload_cache.update({int(event.chat_id): {}})
    if match:
        if not os.path.exists(match):
            return await xx.eor("Файл не существует.")
        _webupload_cache[event.chat_id][event.id] = match
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply.photo:
            file = await reply.download_media("resources/downloads/")
            _webupload_cache[int(event.chat_id)][int(event.id)] = file
        else:
            file, _ = await event.client.fast_downloader(
                reply.document, show_progress=True, event=xx
            )
            _webupload_cache[int(event.chat_id)][int(event.id)] = file.name
    else:
        return await xx.eor("Ответьте на файл или укажите путь к файлу...")
    if not event.client._bot:
        results = await event.client.inline_query(
            asst.me.username, f"fl2lnk {event.chat_id}:{event.id}"
        )
        await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
        await xx.delete()

    else:
        __cache = f"{event.chat_id}:{event.id}"
        buttons = [
            [
                Button.inline("catbox", data=f"flcatbox//{__cache}"),
                Button.inline("transfer", data=f"fltransfer//{__cache}"),
            ],
            [
                Button.inline("filebin", data=f"flfilebin//{__cache}"),
                Button.inline("0x0.st", data=f"fl0x0.st//{__cache}"),
            ],
            [
                Button.inline("file.io", data=f"flfile.io//{__cache}"),
                Button.inline("siasky", data=f"flsiasky//{__cache}"),
            ],
        ]
        await xx.edit("Выберите сервер для загрузки файла...", buttons=buttons)
