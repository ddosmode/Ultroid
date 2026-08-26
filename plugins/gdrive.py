"""
✘ Доступные команды

• `{i}gdul <ответ/имя файла>`
    Ответьте на файл для загрузки в Google Drive.
    Укажите имя файла для загрузки в Google Drive.

• `{i}gdown <id файла/ссылка> | <имя файла>`
    Скачать по ссылке GDrive или id файла.

• `{i}gdsearch <имя файла>`
    Найти имя файла в Google Drive и получить ссылку.

• `{i}gdlist`
    Показать все файлы GDrive.

• `{i}gdfolder`
    Ссылка на вашу папку Google Drive.
    Если задана, все файлы будут загружаться в эту папку.
"""

import os
import time

from telethon.tl.types import Message

from pyUltroid.fns.gDrive import GDriveManager
from pyUltroid.fns.helper import time_formatter

from . import ULTConfig, asst, eod, eor, get_string, ultroid_cmd


@ultroid_cmd(
    pattern="gdown( (.*)|$)",
    fullsudo=True,
)
async def gdown(event):
    GDrive = GDriveManager()
    match = event.pattern_match.group(1).strip()
    if not match:
        return await eod(event, "`Укажите id файла или ссылку GDrive для скачивания!`")
    filename = match.split(" | ")[1].strip() if " | " in match else None
    eve = await event.eor(get_string("com_1"))
    _start = time.time()
    status, response = await GDrive._download_file(eve, match, filename)
    if not status:
        return await eve.edit(response)
    await eve.edit(
        f"`Скачано ``{response}`` за {time_formatter((time.time() - _start)*1000)}`"
    )


@ultroid_cmd(
    pattern="gdlist$",
    fullsudo=True,
)
async def files(event):
    GDrive = GDriveManager()
    if not os.path.exists(GDrive.token_file):
        return await event.eor(get_string("gdrive_6").format(asst.me.username))
    eve = await event.eor(get_string("com_1"))
    msg = ""
    if files := GDrive._list_files:
        msg += f"В GDrive найдено файлов: {len(files.keys())}.\n\n"
        for _ in files:
            msg += f"> [{files[_]}]({_})\n"
    else:
        msg += "В GDrive ничего нет"
    if len(msg) < 4096:
        await eve.edit(msg, link_preview=False)
    else:
        with open("drive-files.txt", "w") as f:
            f.write(
                msg.replace("[", "Имя файла: ")
                .replace("](", "\n» Ссылка: ")
                .replace(")\n", "\n\n")
            )
        try:
            await eve.delete()
        except BaseException:
            pass
        await event.client.send_file(
            event.chat_id,
            "drive-files.txt",
            thumb=ULTConfig.thumb,
            reply_to=event,
        )
        os.remove("drive-files.txt")


@ultroid_cmd(
    pattern="gdul( (.*)|$)",
    fullsudo=True,
)
async def _(event):
    GDrive = GDriveManager()
    if not os.path.exists(GDrive.token_file):
        return await eod(event, get_string("gdrive_6").format(asst.me.username))
    input_file = event.pattern_match.group(1).strip() or await event.get_reply_message()
    if not input_file:
        return await eod(event, "`Ответьте на файл или укажите его расположение.`")
    mone = await event.eor(get_string("com_1"))
    if isinstance(input_file, Message):
        location = "resources/downloads"
        if input_file.photo:
            filename = await input_file.download_media(location)
        else:
            filename = input_file.file.name
            if not filename:
                filename = str(round(time.time()))
            filename = f"{location}/{filename}"
            try:
                filename, downloaded_in = await event.client.fast_downloader(
                    file=input_file.media.document,
                    filename=filename,
                    show_progress=True,
                    event=mone,
                    message=get_string("com_5"),
                )
                filename = filename.name
            except Exception as e:
                return await eor(mone, str(e), time=10)
        await mone.edit(
            f"`Скачано в ``{filename}`.`",
        )
    else:
        filename = input_file.strip()
        if not os.path.exists(filename):
            return await eod(
                mone,
                "Файл не найден на локальном сервере. Укажите путь к файлу :((",
                time=5,
            )
    folder_id = None
    if os.path.isdir(filename):
        files = os.listdir(filename)
        if not files:
            return await eod(
                mone, "`Запрошенная директория пуста. Невозможно создать пустую директорию.`"
            )
        folder_id = GDrive.create_directory(filename)
        c = 0
        for files in sorted(files):
            file = f"{filename}/{files}"
            if not os.path.isdir(file):
                try:
                    await GDrive._upload_file(mone, path=file, folder_id=folder_id)
                    c += 1
                except Exception as e:
                    return await mone.edit(
                        f"При загрузке в GDrive произошла ошибка {e}"
                    )
        return await mone.edit(
            f"`Загружено `[{filename}](https://drive.google.com/folderview?id={folder_id})` — {c} файлов.`"
        )
    try:
        g_drive_link = await GDrive._upload_file(
            mone,
            filename,
        )
        await mone.edit(
            get_string("gdrive_7").format(filename.split("/")[-1], g_drive_link)
        )
    except Exception as e:
        await mone.edit(f"При загрузке в GDrive произошла ошибка {e}")


@ultroid_cmd(
    pattern="gdsearch( (.*)|$)",
    fullsudo=True,
)
async def _(event):
    GDrive = GDriveManager()
    if not os.path.exists(GDrive.token_file):
        return await event.eor(get_string("gdrive_6").format(asst.me.username))
    input_str = event.pattern_match.group(1).strip()
    if not input_str:
        return await event.eor("`Укажите имя файла для поиска в GDrive...`")
    eve = await event.eor(f"`Поиск {input_str} в G-Drive...`")
    files = GDrive.search(input_str)
    msg = ""
    if files:
        msg += (
            f"В GDrive найдено файлов: {len(files.keys())} с {input_str} в названии.\n\n"
        )
        for _ in files:
            msg += f"> [{files[_]}]({_})\n"
    else:
        msg += f"`Нет файлов с названием {input_str}`"
    if len(msg) < 4096:
        await eve.eor(msg, link_preview=False)
    else:
        with open("drive-files.txt", "w") as f:
            f.write(
                msg.replace("[", "Имя файла: ")
                .replace("](", "\n» Ссылка: ")
                .replace(")\n", "\n\n")
            )
        try:
            await eve.delete()
        except BaseException:
            pass
        await event.client.send_file(
            event.chat_id,
            f"{input_str}.txt",
            thumb=ULTConfig.thumb,
            reply_to=event,
        )
        os.remove(f"{input_str}.txt")


@ultroid_cmd(
    pattern="gdfolder$",
    fullsudo=True,
)
async def _(event):
    GDrive = GDriveManager()
    if not os.path.exists(GDrive.token_file):
        return await event.eor(get_string("gdrive_6").format(asst.me.username))
    if GDrive.folder_id:
        await event.eor(
            "`Ссылка на вашу папку G-Drive: `\n"
            + GDrive._create_folder_link(GDrive.folder_id)
        )
    else:
        await eod(event, "Задайте FOLDERID в настройках ассистента ")
