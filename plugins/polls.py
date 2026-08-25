# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, ознакомьтесь с GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}poll <question> ; <option> ; <option>`
    Получить анонимный опрос с заданными вариантами

• `{i}poll <question> ; <option> ; <option> | <type>`
    Получить опрос с указанным желаемым типом!
    тип должен быть одним из  `public`,  `multiple` или `quiz`

• `{i}poll <question> ; <option> ; <option> | quiz_<answerno>`
    Получить викторину, где answerno — это номер правильного варианта

"""
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer, TextWithEntities

from . import get_string, ultroid_cmd


@ultroid_cmd(
    pattern="poll( (.*)|$)",
)
async def uri_poll(e):
    if not e.client._bot and e.is_private:
        return await e.eor("`Используйте это в группе/канале.`", time=15)
    match = e.pattern_match.group(1).strip()
    if not match:
        return await e.eor("`Введите корректные данные...`", time=5)
    if ";" not in match:
        return await e.eor("`Не удалось определить варианты.`.", time=5)
    ques = match.split(";")[0]
    option = match.split(";")[1::]
    publ = None
    quizo = None
    karzo = None
    mpp = None
    if "|" in match:
        ptype = match.split(" | ")[1]
        option = match.split("|")[0].split(";")[1::]
        if "_" in ptype:
            karzo = [str(int(ptype.split("_")[1]) - 1).encode()]
            ptype = ptype.split("_")[0]
        if ptype not in ["public", "quiz", "multiple"]:
            return await e.eor("`Недопустимый тип опроса...`", time=5)
        if ptype == "multiple":
            mpp = True
        elif ptype == "public":
            publ = True
        elif ptype == "quiz":
            quizo = True
    if len(option) <= 1:
        return await e.eor("`Вариантов должно быть больше одного..`", time=5)
    m = await e.eor(get_string("com_1"))
    OUT = [PollAnswer(TextWithEntities(option[on], entities=[]), str(on).encode()) for on in range(len(option))]
    await e.respond(
        file=InputMediaPoll(
            Poll(20, TextWithEntities(ques, entities=[]), OUT, multiple_choice=mpp, public_voters=publ, quiz=quizo),
            correct_answers=karzo,
        ),
    )
    await m.delete()