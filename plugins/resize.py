# Ultroid - UserBot
# Авторские права (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

•`{i}size <ответ на медиа>`
   Чтобы получить его размер.

•`{i}resize <число> <число>`
   Чтобы изменить размер изображения по осям x, y.
   напр. `{i}resize 690 960`
"""
from PIL import Image

from . import HNDLR, eor, get_string, os, ultroid_cmd


@ultroid_cmd(pattern="size$")
async def size(e):
    r = await e.get_reply_message()
    if not (r and r.media):
        return await e.eor(get_string("ascii_1"))
    k = await e.eor(get_string("com_1"))
    if hasattr(r.media, "document"):
        img = await e.client.download_media(r, thumb=-1)
    else:
        img = await r.download_media()
    im = Image.open(img)
    x, y = im.size
    await k.edit(f"Размеры этого изображения\n`{x} x {y}`")
    os.remove(img)


@ultroid_cmd(pattern="resize( (.*)|$)")
async def resize(e):
    r = await e.get_reply_message()
    if not (r and r.media):
        return await e.eor(get_string("ascii_1"))
    sz = e.pattern_match.group(1).strip()
    if not sz:
        return await eor(
            f"Укажите размер для изменения, например `{HNDLR}resize 720 1080` ", time=5
        )
    k = await e.eor(get_string("com_1"))
    if hasattr(r.media, "document"):
        img = await e.client.download_media(r, thumb=-1)
    else:
        img = await r.download_media()
    sz = sz.split()
    if len(sz) != 2:
        return await eor(
            k, f"Укажите размер для изменения, например `{HNDLR}resize 720 1080` ", time=5
        )
    x, y = int(sz[0]), int(sz[1])
    im = Image.open(img)
    ok = im.resize((x, y))
    ok.save(img, format="PNG", optimize=True)
    await e.reply(file=img)
    os.remove(img)
    await k.delete()
