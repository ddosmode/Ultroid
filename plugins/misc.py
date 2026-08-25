# Ultroid - ЮзерБот
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License в
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}eod`
    `Получить событие дня`

• `{i}pntrst <link/id>`
    Скачать и отправить пины Pinterest

• `{i}gadget <search query>`
    Поиск гаджетов в Telegram.

• `{i}randomuser`
   Генерация данных случайного пользователя.

• `{i}ascii <reply image>`
     Конвертировать изображение в HTML.
"""

import os
from datetime import datetime as dt

from bs4 import BeautifulSoup as bs

try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None
try:
    from img2html.converter import Img2HTMLConverter
except ImportError:
    Img2HTMLConverter = None

from . import async_searcher, get_random_user_data, get_string, re, ultroid_cmd


@ultroid_cmd(pattern="eod$")
async def diela(e):
    m = await e.eor(get_string("com_1"))
    li = "https://daysoftheyear.com"
    te = "🎊 **События дня**\n\n"
    da = dt.now()
    month = da.strftime("%b")
    li += f"/days/{month}/" + da.strftime("%F").split("-")[2]
    ct = await async_searcher(li, re_content=True)
    bt = bs(ct, "html.parser", from_encoding="utf-8")
    ml = bt.find_all("a", "js-link-target", href=re.compile("daysoftheyear.com/days"))
    for eve in ml[:5]:
        te += f'• [{eve.text}]({eve["href"]})\n'
    await m.edit(te, link_preview=False)


@ultroid_cmd(
    pattern="pntrst( (.*)|$)",
)
async def pinterest(e):
    m = e.pattern_match.group(1).strip()
    if not m:
        return await e.eor("`Укажите ссылку Pinterest.`", time=3)
    soup = await async_searcher(
        "https://www.expertstool.com/download-pinterest-video/",
        data={"url": m},
        post=True,
    )
    try:
        _soup = bs(soup, "html.parser").find("table").tbody.find_all("tr")
    except BaseException:
        return await e.eor("`Неверная ссылка или закрытый пин.`", time=5)
    file = _soup[1] if len(_soup) > 1 else _soup[0]
    file = file.td.a["href"]
    await e.client.send_file(e.chat_id, file, caption=f"Пин:- {m}")


@ultroid_cmd(pattern="gadget( (.*)|$)")
async def mobs(e):
    mat = e.pattern_match.group(1).strip()
    if not mat:
        await e.eor("Пожалуйста, укажите название мобильного устройства для поиска.")
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = await async_searcher(jwala)
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await e.eor("Результаты не найдены!")
    bt = await e.eor(get_string("com_1"))
    out = "**📱 Поиск мобильных / гаджетов**\n\n"
    li = co[0].find("a")
    imu, title = None, li.find("img")["title"]
    cont = await async_searcher(li["href"])
    nu = bs(cont, "html.parser", from_encoding="utf-8")
    req = nu.find_all("div", "_pdsd")
    imu = nu.find_all(
        "img", src=re.compile("https://i.gadgets360cdn.com/products/large/")
    )
    if imu:
        imu = imu[0]["src"].split("?")[0] + "?downsize=*:420&output-quality=80"
    out += f"☑️ **[{title}]({li['href']})**\n\n"
    for fp in req:
        ty = fp.findNext()
        out += f"- **{ty.text}** - `{ty.findNext().text}`\n"
    out += "_"
    if imu == []:
        imu = None
    await e.reply(out, file=imu, link_preview=False)
    await bt.delete()


@ultroid_cmd(pattern="randomuser")
async def _gen_data(event):
    x = await event.eor(get_string("com_1"))
    msg, pic = await get_random_user_data()
    await event.reply(file=pic, message=msg)
    await x.delete()


@ultroid_cmd(
    pattern="ascii( (.*)|$)",
)
async def _(e):
    if not Img2HTMLConverter:
        return await e.eor("'img2html-converter' не установлен!")
    if not e.reply_to_msg_id:
        return await e.eor(get_string("ascii_1"))
    m = await e.eor(get_string("ascii_2"))
    img = await (await e.get_reply_message()).download_media()
    char = e.pattern_match.group(1).strip() or "■"
    converter = Img2HTMLConverter(char=char)
    html = converter.convert(img)
    shot = WebShot(quality=85)
    pic = await shot.create_pic_async(html=html)
    await m.delete()
    await e.reply(file=pic)
    os.remove(pic)
    os.remove(img)
