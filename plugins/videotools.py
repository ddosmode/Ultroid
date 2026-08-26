"""
✘ Доступные команды -

•`{i}sample <duration in seconds>`
   Создаёт короткий фрагмент видео..

• `{i}vshots <number of shots>`
   Создаёт скриншот видео..

• `{i}vtrim <start time> - <end time> in seconds`
    Обрезать длинное видео..
"""

import glob
import os

from pyUltroid.fns.tools import set_attributes

from . import (
    ULTConfig,
    bash,
    duration_s,
    eod,
    genss,
    get_string,
    mediainfo,
    stdr,
    ultroid_cmd,
)


@ultroid_cmd(pattern="sample( (.*)|$)")
async def gen_sample(e):
    sec = e.pattern_match.group(1).strip()
    stime = int(sec) if sec and sec.isdigit() else 30
    vido = await e.get_reply_message()
    if vido and vido.media and "video" in mediainfo(vido.media):
        msg = await e.eor(get_string("com_1"))
        file, _ = await e.client.fast_downloader(
            vido.document, show_progress=True, event=msg
        )
        file_name = (file.name).split("/")[-1]
        out = file_name.replace(file_name.split(".")[-1], "_sample.mkv")
        xxx = await msg.edit(f"Создание образца длительностью `{stime}` секунд...")
        ss, dd = await duration_s(file.name, stime)
        cmd = f'ffmpeg -i "{file.name}" -preset ultrafast -ss {ss} -to {dd} -codec copy -map 0 "{out}" -y'
        await bash(cmd)
        os.remove(file.name)
        attributes = await set_attributes(out)
        mmmm, _ = await e.client.fast_uploader(
            out, show_progress=True, event=xxx, to_delete=True
        )
        caption = f"Образец видео длительностью `{stime}` секунд"
        await e.client.send_file(
            e.chat_id,
            mmmm,
            thumb=ULTConfig.thumb,
            caption=caption,
            attributes=attributes,
            force_document=False,
            reply_to=e.reply_to_msg_id,
        )
        await xxx.delete()
    else:
        await e.eor(get_string("audiotools_8"), time=5)


@ultroid_cmd(pattern="vshots( (.*)|$)")
async def gen_shots(e):
    ss = e.pattern_match.group(1).strip()
    shot = int(ss) if ss and ss.isdigit() else 5
    vido = await e.get_reply_message()
    if vido and vido.media and "video" in mediainfo(vido.media):
        msg = await e.eor(get_string("com_1"))
        file, _ = await e.client.fast_downloader(
            vido.document, show_progress=True, event=msg
        )
        xxx = await msg.edit(f"Создание `{shot}` скриншотов...")
        await bash("rm -rf ss && mkdir ss")
        cmd = f'ffmpeg -i "{file.name}" -vf fps=0.009 -vframes {shot} "ss/pic%01d.png"'
        await bash(cmd)
        os.remove(file.name)
        pic = glob.glob("ss/*")
        text = f"Загружено {len(pic)}/{shot} скриншотов"
        if not pic:
            text = "`Не удалось сделать скриншоты..`"
            pic = None
        await e.respond(text, file=pic)
        await bash("rm -rf ss")
        await xxx.delete()


@ultroid_cmd(pattern="vtrim( (.*)|$)")
async def gen_sample(e):
    sec = e.pattern_match.group(1).strip()
    if not sec or "-" not in sec:
        return await eod(e, get_string("audiotools_3"))
    a, b = sec.split("-")
    if int(a) >= int(b):
        return await eod(e, get_string("audiotools_4"))
    vido = await e.get_reply_message()
    if vido and vido.media and "video" in mediainfo(vido.media):
        msg = await e.eor(get_string("audiotools_5"))
        file, _ = await e.client.fast_downloader(
            vido.document, show_progress=True, event=msg
        )
        file_name = (file.name).split("/")[-1]
        out = file_name.replace(file_name.split(".")[-1], "_trimmed.mkv")
        if int(b) > int(await genss(file.name)):
            os.remove(file.name)
            return await eod(msg, get_string("audiotools_6"))
        ss, dd = stdr(int(a)), stdr(int(b))
        xxx = await msg.edit(f"Обрезка видео с `{ss}` до `{dd}`...")
        cmd = f'ffmpeg -i "{file.name}" -preset ultrafast -ss {ss} -to {dd} -codec copy -map 0 "{out}" -y'
        await bash(cmd)
        os.remove(file.name)
        attributes = await set_attributes(out)
        mmmm, _ = await e.client.fast_uploader(
            out, show_progress=True, event=msg, to_delete=True
        )
        caption = f"Обрезано видео с `{ss}` до `{dd}`"
        await e.client.send_file(
            e.chat_id,
            mmmm,
            thumb=ULTConfig.thumb,
            caption=caption,
            attributes=attributes,
            force_document=False,
            reply_to=e.reply_to_msg_id,
        )
        await xxx.delete()
    else:
        await e.eor(get_string("audiotools_8"), time=5)
