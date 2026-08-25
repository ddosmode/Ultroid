# Ultroid - UserBot
# Авторские права (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Доступные команды -

• `{i}lock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>`
    Заблокировать используемую настройку в группе.

• `{i}unlock <msgs/media/sticker/gif/games/inline/polls/invites/pin/changeinfo>`
    РАЗБЛОКИРОВАТЬ используемую настройку в группе.
"""
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest

from pyUltroid.fns.admins import lock_unlock

from . import ultroid_cmd


@ultroid_cmd(
    pattern="(un|)lock( (.*)|$)", admins_only=True, manager=True, require="change_info"
)
async def un_lock(e):
    mat = e.pattern_match.group(2).strip()
    if not mat:
        return await e.eor("`Укажите корректный параметр..`", time=5)
    lock = e.pattern_match.group(1) == ""
    ml = lock_unlock(mat, lock)
    if not ml:
        return await e.eor("`Некорректный ввод`", time=5)
    msg = "Заблокировано" if lock else "Разблокировано"
    try:
        await e.client(EditChatDefaultBannedRightsRequest(e.chat_id, ml))
    except Exception as er:
        return await e.eor(str(er))
    await e.eor(f"**{msg}** - `{mat}` ! ")
