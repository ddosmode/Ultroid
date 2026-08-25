# Ultroid - ЮзерБот
# Авторское право (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочитайте GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from . import get_help

__doc__ = get_help("help_database")


import re

from . import Redis, eor, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="setdb( (.*)|$)", fullsudo=True)
async def _(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("Укажите ключ и значение для установки!")
    try:
        delim = " " if re.search("[|]", match) is None else " | "
        data = match.split(delim, maxsplit=1)
        if data[0] in ["--extend", "-e"]:
            data = data[1].split(maxsplit=1)
            data[1] = f"{str(udB.get_key(data[0]))} {data[1]}"
        udB.set_key(data[0], data[1])
        await ult.eor(
            f"**Пара ключ-значение БД обновлена\nКлюч :** `{data[0]}`\n**Значение :** `{data[1]}`"
        )

    except BaseException:
        await ult.eor(get_string("com_7"))


@ultroid_cmd(pattern="deldb( (.*)|$)", fullsudo=True)
async def _(ult):
    key = ult.pattern_match.group(1).strip()
    if not key:
        return await ult.eor("Укажите имя ключа для удаления!", time=5)
    _ = key.split(maxsplit=1)
    try:
        if _[0] == "-m":
            for key in _[1].split():
                k = udB.del_key(key)
            key = _[1]
        else:
            k = udB.del_key(key)
        if k == 0:
            return await ult.eor("`Такой ключ не найден.`")
        await ult.eor(f"`Ключ {key} успешно удалён`")
    except BaseException:
        await ult.eor(get_string("com_7"))


@ultroid_cmd(pattern="rendb( (.*)|$)", fullsudo=True)
async def _(ult):
    match = ult.pattern_match.group(1).strip()
    if not match:
        return await ult.eor("`Укажите имя ключа для переименования..`")
    delim = " " if re.search("[|]", match) is None else " | "
    data = match.split(delim)
    if Redis(data[0]):
        try:
            udB.rename(data[0], data[1])
            await eor(
                ult,
                f"**Переименование ключа БД успешно\nСтарый ключ :** `{data[0]}`\n**Новый ключ :** `{data[1]}`",
            )

        except BaseException:
            await ult.eor(get_string("com_7"))
    else:
        await ult.eor("Ключ не найден")
