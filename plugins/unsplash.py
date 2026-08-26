# TeleFriend - ЮзерБот
# Авторское право (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• {i}unsplash <поисковый запрос> ; <кол-во изображений>
    Поиск изображений через Unsplash.
"""

from pyUltroid.fns.misc import unsplashsearch

from . import asyncio, download_file, get_string, os, ultroid_cmd


@ultroid_cmd(pattern="unsplash( (.*)|$)")
async def searchunsl(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("Дай мне что-нибудь для поиска")
    num = 5
    if ";" in match:
        num = int(match.split(";")[1])
        match = match.split(";")[0]
    tep = await ult.eor(get_string("com_1"))
    res = await unsplashsearch(match, limit=num)
    if not res:
        return await ult.eor(get_string("unspl_1"), time=5)
    CL = [download_file(rp, f"{match}-{e}.png") for e, rp in enumerate(res)]
    imgs = [z[0] for z in (await asyncio.gather(*CL)) if z]
    await ult.respond(f"Загружено {len(imgs)} изображений!", file=imgs)
    await tep.delete()
    [os.remove(img) for img in imgs]
