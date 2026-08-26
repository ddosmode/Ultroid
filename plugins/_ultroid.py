from telethon.errors import (
    BotMethodInvalidError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
)

from . import LOG_CHANNEL, LOGS, Button, asst, eor, get_string, ultroid_cmd

REPOMSG = """
• **ULTROID USERBOT** •\n
• Репозиторий - [Нажмите здесь](https://github.com/TeamTeleFriend/TeleFriend)
• Дополнения - [Нажмите здесь](https://github.com/TeamTeleFriend/TeleFriendAddons)
• Поддержка - @TeleFriendSupportChat
"""

RP_BUTTONS = [
    [
        Button.url(get_string("bot_3"), "https://github.com/TeamTeleFriend/TeleFriend"),
        Button.url("Дополнения", "https://github.com/TeamTeleFriend/TeleFriendAddons"),
    ],
    [Button.url("Группа поддержки", "t.me/TeleFriendSupportChat")],
]

ULTSTRING = """🎇 **Спасибо за развёртывание TeleFriend Userbot!**

• Здесь представлены некоторые основные сведения о его использовании."""


@ultroid_cmd(
    pattern="repo$",
    manager=True,
)
async def repify(e):
    try:
        q = await e.client.inline_query(asst.me.username, "")
        await q[0].click(e.chat_id)
        return await e.delete()
    except (
        ChatSendInlineForbiddenError,
        ChatSendMediaForbiddenError,
        BotMethodInvalidError,
    ):
        pass
    except Exception as er:
        LOGS.info(f"Ошибка при выполнении команды repo : {str(er)}")
    await e.eor(REPOMSG)


@ultroid_cmd(pattern="ultroid$")
async def useTeleFriend(rs):
    button = Button.inline("Начать >>", "initft_2")
    msg = await asst.send_message(
        LOG_CHANNEL,
        ULTSTRING,
        file="https://graph.org/file/54a917cc9dbb94733ea5f.jpg",
        buttons=button,
    )
    if not (rs.chat_id == LOG_CHANNEL and rs.client._bot):
        await eor(rs, f"**[Нажмите здесь]({msg.message_link})**")
