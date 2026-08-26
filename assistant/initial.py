# TeleFriend - Пользовательский бот
# Авторские права (C) 2021-2026 TeamTeleFriend
#
# Этот файл является частью < https://github.com/TeamTeleFriend/TeleFriend/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamTeleFriend/TeleFriend/blob/main/LICENSE/>.

import re

from . import *

STRINGS = {
    1: """🎇 **Спасибо за развертывание TeleFriend Userbot!**

• Вот некоторые основные моменты, из которых вы можете узнать об использовании.""",
    2: """🎉** Об TeleFriend**

🧿 TeleFriend — это модульный и мощный Telethon Userbot, созданный на Python с нуля. Он направлен на повышение безопасности вместе с добавлением других полезных функций.

❣ Сделано **@TeamTeleFriend**""",
    3: """**💡• ЧаВо •**

-> [Трекер юзернеймов](https://t.me/TeleFriendUpdates/24)
-> [Хранение репо с кастомными аддонами](https://t.me/TeleFriendUpdates/28)
-> [Отключение сообщения о деплое](https://t.me/TeleFriendUpdates/27)
-> [Настройка часового пояса](https://t.me/TeleFriendUpdates/22)
-> [Об Inline PmPermit](https://t.me/TeleFriendUpdates/21)
-> [О Dual Mode](https://t.me/TeleFriendUpdates/18)
-> [Кастомная миниатюра](https://t.me/TeleFriendUpdates/13)
-> [О FullSudo](https://t.me/TeleFriendUpdates/11)
-> [Настройка PmBot](https://t.me/TeleFriendUpdates/2)
-> [Также проверьте](https://t.me/TeleFriendUpdates/14)

**• Чтобы узнать об обновлениях**
  - Вступите в @TeamTeleFriend.""",
    4: f"""• `Чтобы узнать все доступные команды`

  - `{HNDLR}help`
  - `{HNDLR}cmds`""",
    5: """• **По любым другим вопросам или предложениям**
  - Перейдите в **@TeleFriendSupportChat**.

• Спасибо, что дошли до конца.""",
}


@callback(re.compile("initft_(\\d+)"))
async def init_depl(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 5:
        return await e.edit(
            STRINGS[5],
            buttons=Button.inline("<< Назад", "initbk_4"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )


@callback(re.compile("initbk_(\\d+)"))
async def ineiq(e):
    CURRENT = int(e.data_match.group(1))
    if CURRENT == 1:
        return await e.edit(
            STRINGS[1],
            buttons=Button.inline("В начало >>", "initft_2"),
            link_preview=False,
        )

    await e.edit(
        STRINGS[CURRENT],
        buttons=[
            Button.inline("<<", f"initbk_{str(CURRENT - 1)}"),
            Button.inline(">>", f"initft_{str(CURRENT + 1)}"),
        ],
        link_preview=False,
    )
