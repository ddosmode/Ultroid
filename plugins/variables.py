# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License:
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}get var <variable name>`
   Получить значение переменной с указанным именем.

• `{i}get type <variable name>`
   Получить тип переменной.

• `{i}get db <key>`
   Получить значение из базы данных по указанному ключу.

• `{i}get keys`
   Получить все ключи redis.
"""

import os

from . import eor, get_string, udB, ultroid_cmd, HNDLR


@ultroid_cmd(pattern="get($| (.*))", fullsudo=True)
async def get_var(event):
    try:
        opt = event.text.split(maxsplit=2)[1]
    except IndexError:
        return await event.eor(f"Что получить?\nИспользуйте `{HNDLR}help variables`")
    x = await event.eor(get_string("com_1"))
    if opt != "keys":
        try:
            varname = event.text.split(maxsplit=2)[2]
        except IndexError:
            return await eor(x, "Такой переменной не существует!", time=5)
    if opt == "var":
        c = 0
        # пробуем redis
        val = udB.get_key(varname)
        if val is not None:
            c += 1
            await x.edit(
                f"**Переменная** - `{varname}`\n**Значение**: `{val}`\n**Тип**: Ключ Redis."
            )
        # пробуем переменные окружения
        val = os.getenv(varname)
        if val is not None:
            c += 1
            await x.edit(
                f"**Переменная** - `{varname}`\n**Значение**: `{val}`\n**Тип**: Переменная окружения."
            )

        if c == 0:
            await eor(x, "Такой переменной не существует!", time=5)

    elif opt == "type":
        c = 0
        # пробуем redis
        val = udB.get_key(varname)
        if val is not None:
            c += 1
            await x.edit(f"**Переменная** - `{varname}`\n**Тип**: Ключ Redis.")
        # пробуем переменные окружения
        val = os.getenv(varname)
        if val is not None:
            c += 1
            await x.edit(f"**Переменная** - `{varname}`\n**Тип**: Переменная окружения.")

        if c == 0:
            await eor(x, "Такой переменной не существует!", time=5)

    elif opt == "db":
        val = udB.get(varname)
        if val is not None:
            await x.edit(f"**Ключ** - `{varname}`\n**Значение**: `{val}`")
        else:
            await eor(x, "Такой ключ не найден!", time=5)

    elif opt == "keys":
        keys = sorted(udB.keys())
        msg = "".join(
            f"• `{i}`" + "\n"
            for i in keys
            if not i.isdigit()
            and not i.startswith("-")
            and not i.startswith("_")
            and not i.startswith("GBAN_REASON_")
        )

        await x.edit(f"**Список ключей БД :**\n{msg}")
