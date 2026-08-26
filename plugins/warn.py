"""
✘ Доступные команды

•`{i}warn <ответить пользователю> <причина>`
    Выдаёт предупреждение.

•`{i}resetwarn <ответить пользователю>`
    Сбросить все предупреждения.

•`{i}warns <ответить пользователю>`
   Получить список предупреждений пользователя.

•`{i}setwarn <количество предупреждений> | <ban/mute/kick>`
   Установить число предупреждений
   После знака " | " укажите действие, например ban/mute/kick
   По умолчанию 3 kick
   Пример : `setwarn 5 | mute`

"""

from pyUltroid.dB.warn_db import add_warn, reset_warn, warns

from . import eor, get_string, inline_mention, udB, ultroid_cmd


@ultroid_cmd(
    pattern="warn( (.*)|$)",
    manager=True,
    groups_only=True,
    admins_only=True,
)
async def warn(e):
    ultroid_bot = e.client
    reply = await e.get_reply_message()
    if len(e.text) > 5 and " " not in e.text[5]:
        return
    if reply:
        user = reply.sender_id
        reason = e.text[5:] if e.pattern_match.group(1).strip() else "неизвестно"
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await ultroid_bot.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await e.eor("Ответьте пользователю", time=5)
        try:
            reason = e.text.split(maxsplit=2)[-1]
        except BaseException:
            reason = "неизвестно"
    count, r = warns(e.chat_id, user)
    r = f"{r}|$|{reason}" if r else reason
    try:
        x = udB.get_key("SETWARN")
        number, action = int(x.split()[0]), x.split()[1]
    except BaseException:
        number, action = 3, "kick"
    if ("ban" or "kick" or "mute") not in action:
        action = "kick"
    if count + 1 >= number:
        if "ban" in action:
            try:
                await ultroid_bot.edit_permissions(e.chat_id, user, view_messages=False)
            except BaseException:
                return await e.eor("`Что-то пошло не так.`", time=5)
        elif "kick" in action:
            try:
                await ultroid_bot.kick_participant(e.chat_id, user)
            except BaseException:
                return await e.eor("`Что-то пошло не так.`", time=5)
        elif "mute" in action:
            try:
                await ultroid_bot.edit_permissions(
                    e.chat_id, user, until_date=None, send_messages=False
                )
            except BaseException:
                return await e.eor("`Что-то пошло не так.`", time=5)
        add_warn(e.chat_id, user, count + 1, r)
        c, r = warns(e.chat_id, user)
        ok = await ultroid_bot.get_entity(user)
        user = inline_mention(ok)
        r = r.split("|$|")
        text = f"Пользователь {user} получил {action} за {count+1} предупреждений.\n\n"
        for x in range(c):
            text += f"•**{x+1}.** {r[x]}\n"
        await e.eor(text)
        return reset_warn(e.chat_id, ok.id)
    add_warn(e.chat_id, user, count + 1, r)
    ok = await ultroid_bot.get_entity(user)
    user = inline_mention(ok)
    await eor(
        e,
        f"**ПРЕДУПРЕЖДЕНИЕ :** {count+1}/{number}\n**Кому :**{user}\n**Будьте осторожны !!!**\n\n**Причина** : {reason}",
    )


@ultroid_cmd(
    pattern="resetwarn( (.*)|$)",
    manager=True,
    groups_only=True,
    admins_only=True,
)
async def rwarn(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.sender_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await e.eor("Ответьте пользователю")
    reset_warn(e.chat_id, user)
    ok = await e.client.get_entity(user)
    user = inline_mention(ok)
    await e.eor(f"Очищены все предупреждения пользователя {user}.")


@ultroid_cmd(
    pattern="warns( (.*)|$)",
    manager=True,
    groups_only=True,
    admins_only=True,
)
async def twarns(e):
    reply = await e.get_reply_message()
    if reply:
        user = reply.from_id.user_id
    else:
        try:
            user = e.text.split()[1]
            if user.startswith("@"):
                ok = await e.client.get_entity(user)
                user = ok.id
            else:
                user = int(user)
        except BaseException:
            return await e.eor("Ответьте пользователю", time=5)
    c, r = warns(e.chat_id, user)
    if c and r:
        ok = await e.client.get_entity(user)
        user = inline_mention(ok)
        r = r.split("|$|")
        text = f"Пользователь {user} получил {c} предупреждений.\n\n"
        for x in range(c):
            text += f"•**{x+1}.** {r[x]}\n"
        await e.eor(text)
    else:
        await e.eor("`Нет предупреждений`")


@ultroid_cmd(pattern="setwarn( (.*)|$)", manager=True)
async def warnset(e):
    ok = e.pattern_match.group(1).strip()
    if not ok:
        return await e.eor("Неверный формат. Правильное использование: .setwarns <число>|<действие>")
    if "|" in ok:
        try:
            number, action = ok.split("|")
            number = int(number.strip())
            action = action.strip()
        except ValueError:
            return await e.eor(
                "Неверный формат. Правильное использование: .setwarns <число>|<действие>", time=5
            )
        if action not in ["ban", "mute", "kick"]:
            return await e.eor("Поддерживаются только опции mute / ban / kick", time=5)
        udB.set_key("SETWARN", f"{number} {action}")
        await e.eor(f"Готово. Ваше количество предупреждений: {number}, действие: {action}")
    else:
        await e.eor(
            "Неверный формат. Правильное использование: .setwarns <число>|<действие>", time=5
        )
