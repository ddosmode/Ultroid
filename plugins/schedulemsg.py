# TeleFriend - UserBot
# Авторские права (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License по адресу
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.
"""
✘ Доступные команды -

•`{i}schedule <текст/ответ на сообщение> <время>`
    Во времени можно указать секунды как число, или например 1h или 1m
    напр. `{i}schedule Hello 100` Отправит сообщение через 100 секунд.
    напр. `{i}schedule Hello 1h` Отправит сообщение через час.
"""
from datetime import timedelta

from pyUltroid.fns.admins import ban_time

from . import get_string, ultroid_cmd


@ultroid_cmd(pattern="schedule( (.*)|$)", fullsudo=True)
async def _(e):
    x = e.pattern_match.group(1).strip()
    xx = await e.get_reply_message()
    if x and not xx:
        y = x.split(" ")[-1]
        k = x.replace(y, "")
        if y.isdigit():
            await e.client.send_message(
                e.chat_id, k, schedule=timedelta(seconds=int(y))
            )
            await e.eor(get_string("schdl_1"), time=5)
        else:
            try:
                z = ban_time(y)
                await e.respond(k, schedule=z)
                await e.eor(get_string("schdl_1"), time=5)
            except BaseException:
                await e.eor(get_string("schdl_2"), time=5)
    elif xx and x:
        if x.isdigit():
            await e.respond(xx, schedule=timedelta(seconds=int(x)))
            await e.eor(get_string("schdl_1"), time=5)
        else:
            try:
                z = ban_time(x)
                await e.respond(xx, schedule=z)
                await e.eor(get_string("schdl_1"), time=5)
            except BaseException:
                await e.eor(get_string("schdl_2"), time=5)
    else:
        return await e.eor(get_string("schdl_2"), time=5)
