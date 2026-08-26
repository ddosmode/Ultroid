from . import *

START = """
🪅 **Меню помощи** 🪅

✘  /start : Проверить, работаю ли я.
✘  /help : Получить это сообщение.
✘  /repo : Получить репозиторий бота..

🧑‍💻 Присоединяйтесь к **@TeamTeleFriend**
"""

ADMINTOOLS = """✘ **Инструменты администрирования** ✘

• /pin : Закрепить ответное сообщение
• /pinned : Получить закреплённое сообщение в чате.
• /unpin : Открепить ответное сообщение
• /unpin all : Открепить все закреплённые сообщения.

• /ban (имя пользователя/id/ответ) : Забанить пользователя
• /unban (имя пользователя/id/ответ) : Разбанить пользователя.

• /mute (имя пользователя/id/ответ) : Заглушить пользователя.
• /unmute (имя пользователя/id/ответ) : Снять заглушение с пользователя.

• /tban (имя пользователя/id/ответ) (время) : Временно забанить пользователя
• /tmute (имя пользователя/id/ответ) (время) : Временно заглушить пользователя.

• /purge (сообщения для очистки)

• /setgpic (ответ фото) : установить фото группы.
• /delgpic : удалить текущее фото чата."""

UTILITIES = """
✘ ** Утилиты ** ✘

• /info (ответ/имя пользователя/id) : получить подробную информацию о пользователе.
• /id : получить id чата/пользователя.
• /tr : Перевести языки..
• /q : Создать цитаты.

• /paste (ответ файл/текст) : вставить содержимое на Spaceb.in
• /meaning (текст) : Получить значение этого слова.
• /google (запрос) : Поискать что-то в Google..

• /suggest (запрос/ответ) : Создать опрос Да / Нет.
"""

LOCKS = """
✘ ** Блокировки ** ✘

• /lock (запрос) : заблокировать определённый контент в чате.
• /unlock (запрос) : Разблокировать контент.

• Все запросы
- `msgs` : для сообщений.
- `inlines` : для встроенных запросов.
- `media` : для всех медиа.
- `games` : для игр.
- `sticker` : для стикеров.
- `polls` : для опросов.
- `gif` : для гифок.
- `pin` : для закреплений.
- `changeinfo` : для права изменения информации.
"""

MISC = """
✘  **Разное**  ✘

• /joke : Получить случайные шутки.
• /decide : Решить что-то..

**✘ Инструменты стикеров ✘**
• /kang : добавить стикер в ваш набор.
• /listpack : получить все ваши наборы..
"""

STRINGS = {"Admintools": ADMINTOOLS, "locks": LOCKS, "Utils": UTILITIES, "Misc": MISC}

MNGE = udB.get_key("MNGR_EMOJI") or "•"


def get_buttons():
    BTTS = []
    keys = STRINGS.copy()
    while keys:
        BT = []
        for i in list(keys)[:2]:
            text = f"{MNGE} {i} {MNGE}"
            BT.append(Button.inline(text, f"hlp_{i}"))
            del keys[i]
        BTTS.append(BT)
    url = f"https://t.me/{asst.me.username}?startgroup=true"
    BTTS.append([Button.url("Добавить меня в группу", url)])
    return BTTS


@asst_cmd(pattern="help")
async def helpish(event):
    if not event.is_private:
        url = f"https://t.me/{asst.me.username}?start=start"
        return await event.reply(
            "Напишите мне в личные сообщения для помощи!", buttons=Button.url("Нажмите для помощи", url)
        )
    if str(event.sender_id) in owner_and_sudos() and (
        udB.get_key("DUAL_MODE") and (udB.get_key("DUAL_HNDLR") == "/")
    ):
        return
    await event.reply(START, buttons=get_buttons())


@callback("mngbtn", owner=True)
async def ehwhshd(e):
    buttons = get_buttons()
    buttons.append([Button.inline("<< Назад", "open")])
    await e.edit(buttons=buttons)


@callback("mnghome")
async def home_aja(e):
    await e.edit(START, buttons=get_buttons())


@callback(re.compile("hlp_(.*)"))
async def do_something(event):
    match = event.pattern_match.group(1).strip().decode("utf-8")
    await event.edit(STRINGS[match], buttons=Button.inline("<< Назад", "mnghome"))