# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}wspr <username>`
    Отправить секретное сообщение..

• `{i}q <color-optional>`
• `{i}q @username`
• `{i}q r <color-optional>`
• `{i}q count` : `несколько цитат`
    Создать цитаты..

• `{i}sticker <query>`
    Искать стикеры по вашему запросу..

• `{i}getaudio <reply to an audio>`
    Скачать аудио, чтобы вставить в нужное видео/гиф.

• `{i}addaudio <reply to Video/gif>`
    Добавит аудио из ответа к прикреплённому видео/гиф.

• `{i}dob <date of birth>`
    Введите в формате дд/мм/гг (напр. .dob 01/01/1999).

• `{i}wall <query>`
    Искать HD обои по вашему запросу..
"""
import os
import time
from datetime import datetime as dt
from random import choice

import pytz, asyncio
from bs4 import BeautifulSoup as bs
from telethon.tl.types import DocumentAttributeVideo
from requests import Session
from cloudscraper import create_scraper
from pyUltroid.fns.tools import get_google_images, metadata

from . import (
    HNDLR,
    ULTConfig,
    async_searcher,
    bash,
    downloader,
    eod,
    get_string,
    mediainfo,
    quotly,
    ultroid_bot,
    ultroid_cmd,
    uploader,
)
from .beautify import all_col

File = []
scraper = create_scraper()

@ultroid_cmd(
    pattern="getaudio$",
)
async def daudtoid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_1"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith(("audio", "video")):
        return await eod(e, get_string("spcltool_1"))
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Загружаю {dl}...",
    )

    File.append(file.name)
    await xxx.edit(get_string("spcltool_2"))


@ultroid_cmd(
    pattern="addaudio$",
)
async def adaudroid(e):
    if not e.reply_to:
        return await eod(e, get_string("spcltool_3"))
    r = await e.get_reply_message()
    if not mediainfo(r.media).startswith("video"):
        return await eod(e, get_string("spcltool_3"))
    if not (File and os.path.exists(File[0])):
        return await e.edit(f"`Сначала ответьте на аудио с помощью {HNDLR}addaudio`")
    xxx = await e.eor(get_string("com_1"))
    dl = r.file.name or "input.mp4"
    c_time = time.time()
    file = await downloader(
        f"resources/downloads/{dl}",
        r.media.document,
        xxx,
        c_time,
        f"Загружаю {dl}...",
    )

    await xxx.edit(get_string("spcltool_5"))
    await bash(
        f'ffmpeg -i "{file.name}" -i "{File[0]}" -shortest -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4'
    )
    out = "output.mp4"
    mmmm = await uploader(out, out, time.time(), xxx, f"Выгружаю {out}...")
    data = await metadata(out)
    width = data["width"]
    height = data["height"]
    duration = data["duration"]
    attributes = [
        DocumentAttributeVideo(
            duration=duration, w=width, h=height, supports_streaming=True
        )
    ]
    await e.client.send_file(
        e.chat_id,
        mmmm,
        thumb=ULTConfig.thumb,
        attributes=attributes,
        force_document=False,
        reply_to=e.reply_to_msg_id,
    )
    await xxx.delete()
    os.remove(out)
    os.remove(file.name)
    File.clear()
    os.remove(File[0])


@ultroid_cmd(
    pattern=r"dob( (.*)|$)",
)
async def hbd(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor(get_string("spcltool_6"))
    if event.reply_to_msg_id:
        kk = await event.get_reply_message()
        nam = await kk.get_sender()
        name = nam.first_name
    else:
        name = ultroid_bot.me.first_name
    zn = pytz.timezone("Asia/Kolkata")
    abhi = dt.now(zn)
    kk = match.split("/")
    p = kk[0]
    r = kk[1]
    s = kk[2]
    day = int(p)
    month = r
    try:
        jn = dt.strptime(match, "%d/%m/%Y")
    except BaseException:
        return await event.eor(get_string("spcltool_6"))
    jnm = zn.localize(jn)
    zinda = abhi - jnm
    barsh = (zinda.total_seconds()) / (365.242 * 24 * 3600)
    saal = int(barsh)
    mash = (barsh - saal) * 12
    mahina = int(mash)
    divas = (mash - mahina) * (365.242 / 12)
    din = int(divas)
    samay = (divas - din) * 24
    ghanta = int(samay)
    pehl = (samay - ghanta) * 60
    mi = int(pehl)
    sec = (pehl - mi) * 60
    slive = int(sec)
    y = int(s) + saal + 1
    m = int(r)
    brth = dt(y, m, day)
    cm = dt(abhi.year, brth.month, brth.day)
    ish = (cm - abhi.today()).days + 1
    dan = ish
    if dan == 0:
        hp = "`С днём рождения🎉🎊`"
    elif dan < 0:
        okk = 365 + ish
        hp = f"Осталось {okk} дней 🥳"
    elif dan > 0:
        hp = f"Осталось {ish} дней 🥳"
    if month == "01":
        sign = "Козерог" if (day < 20) else "Водолей"
    elif month == "02":
        sign = "Водолей" if (day < 19) else "Рыбы"
    elif month == "03":
        sign = "Рыбы" if (day < 21) else "Овен"
    elif month == "04":
        sign = "Овен" if (day < 20) else "Телец"
    elif month == "05":
        sign = "Телец" if (day < 21) else "Близнецы"
    elif month == "06":
        sign = "Близнецы" if (day < 21) else "Рак"
    elif month == "07":
        sign = "Рак" if (day < 23) else "Лев"
    elif month == "08":
        sign = "Лев" if (day < 23) else "Дева"
    elif month == "09":
        sign = "Дева" if (day < 23) else "Весы"
    elif month == "10":
        sign = "Весы" if (day < 23) else "Скорпион"
    elif month == "11":
        sign = "Скорпион" if (day < 22) else "Стрелец"
    elif month == "12":
        sign = "Стрелец" if (day < 22) else "Козерог"
    json = await async_searcher(
        f"https://aztro.sameerkumar.website/?sign={sign}&day=today",
        post=True,
        re_json=True,
    )
    dd = json.get("current_date")
    ds = json.get("description")
    lt = json.get("lucky_time")
    md = json.get("mood")
    cl = json.get("color")
    ln = json.get("lucky_number")
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        f"""
    Имя -: {name}

Дата рождения -:  {match}

Прожито -:  {saal}г, {mahina}мес, {din}дн, {ghanta}ч, {mi}мин, {slive}сек

День рождения -: {hp}

Знак зодиака -: {sign}

**Гороскоп на {dd} -**

`{ds}`

    Удачное время :-        {lt}
    Удачное число :-   {ln}
    Удачный цвет :-        {cl}
    Настроение :-                   {md}
    """,
        reply_to=event.reply_to_msg_id,
    )

session = Session()

@ultroid_cmd(pattern="sticker( (.*)|$)")
async def _(event):
    x = event.pattern_match.group(1).strip()
    if not x:
        return await event.eor("`Введите запрос для поиска`")
    uu = await event.eor(get_string("com_1"))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = scraper.get(
                f"https://combot.org/telegram/stickers?q={x}",
                headers=headers
            ).content
            
            # Проверяем, не содержит ли ответ защиту Cloudflare
            if "Just a moment..." in response.decode():
                retry_count += 1
                await asyncio.sleep(2) # Ждём перед повторной попыткой
                continue
                
            z = bs(response, "html.parser")
            packs = z.find_all("a", {"class": "stickerset__title"})
            
            if not packs:
                return await uu.edit(get_string("spcltool_9"))
                
            break # Успех - выходим из цикла
            
        except Exception as er:
            retry_count += 1
            await asyncio.sleep(2)
            continue
    
    if retry_count >= max_retries:
        return await uu.edit("`Не удалось загрузить стикеры после нескольких попыток`")
    try:
        sticks = {}
        for pack in packs:
            href = pack.get("href")
            title = pack.text.strip()
            if href:
                href = f"https://t.me/addstickers/{href.split('/')[-1]}"
                sticks[href] = title

        if not sticks:
            return await uu.edit(get_string("spcltool_9"))

        a = "Дᴏсᴛуᴘныᴇ сᴛиᴋᴇʀы ~\n\n"
        for href, title in sticks.items():
            a += f"<a href={href}>{title}</a>\n"
        await uu.edit(a, parse_mode="html")
        
    except Exception as e:
        await uu.edit(f"`Ошибка: {str(e)}`\nПопробуйте позже.")

@ultroid_cmd(pattern="wall( (.*)|$)")
async def wall(event):
    inp = event.pattern_match.group(1).strip()
    if not inp:
        return await event.eor("`Введите запрос для поиска..`")
    nn = await event.eor(get_string("com_1"))
    query = f"hd {inp}"
    images = await get_google_images(query)
    for z in range(5):
        await event.client.send_file(event.chat_id, file=images[z]["original"])
    await nn.delete()


@ultroid_cmd(pattern="q( (.*)|$)", manager=True, allow_pm=True)
async def quott_(event):
    match = event.pattern_match.group(1).strip()
    if not event.is_reply:
        return await event.eor("`Ответьте на сообщение..`")
    msg = await event.eor(get_string("com_1"))
    reply = await event.get_reply_message()
    replied_to, reply_ = None, None
    if match:
        spli_ = match.split(maxsplit=1)
        if (spli_[0] in ["r", "reply"]) or (
            spli_[0].isdigit() and int(spli_[0]) in range(1, 21)
        ):
            if spli_[0].isdigit():
                if not event.client._bot:
                    reply_ = await event.client.get_messages(
                        event.chat_id,
                        min_id=event.reply_to_msg_id - 1,
                        reverse=True,
                        limit=int(spli_[0]),
                    )
                else:
                    id_ = reply.id
                    reply_ = []
                    for msg_ in range(id_, id_ + int(spli_[0])):
                        msh = await event.client.get_messages(event.chat_id, ids=msg_)
                        if msh:
                            reply_.append(msh)
            else:
                replied_to = await reply.get_reply_message()
            try:
                match = spli_[1]
            except IndexError:
                match = None
    user = None
    if not reply_:
        reply_ = reply
    if match:
        match = match.split(maxsplit=1)
    if match:
        if match[0].startswith("@") or match[0].isdigit():
            try:
                match_ = await event.client.parse_id(match[0])
                user = await event.client.get_entity(match_)
            except ValueError:
                pass
            match = match[1] if len(match) == 2 else None
        else:
            match = match[0]
    if match == "random":
        match = choice(all_col)
    try:
        file = await quotly.create_quotly(
            reply_, bg=match, reply=replied_to, sender=user
        )
    except Exception as er:
        return await msg.edit(str(er))
    message = await reply.reply("Цитата от Ultroid", file=file)
    os.remove(file)
    await msg.delete()
    return message
