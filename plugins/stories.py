# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Доступные команды -

• `{i}setstory <ответ на медиа>`
    Установить медиа в качестве истории.

• `{i}storydl <юзернейм/ответ на пользователя/ссылка на историю>`
    Скачать и загрузить истории пользователя или конкретную историю по ссылке!
"""

import os
import re
from contextlib import suppress
from . import ultroid_cmd, get_string, LOGS

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, UserFull, InputPeerSelf, InputPrivacyValueAllowAll, Channel, InputUserSelf
from telethon.tl.functions.stories import SendStoryRequest, GetStoriesByIDRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.events import NewMessage


@ultroid_cmd("setstory")
async def setStory(event: NewMessage.Event):
    reply = await event.get_reply_message()
    if not (reply and (reply.photo or reply.video)):
        await event.eor("Ответьте на фото или видео!", time=5)
        return
    msg = await event.eor(get_string("com_1"))
    try:
        await event.client(
        SendStoryRequest(
            InputPeerSelf(),
            reply.media,
            privacy_rules=[
             InputPrivacyValueAllowAll()   
            ]
        )
    )
        await msg.eor("🔥 **История опубликована!**", time=5)
    except Exception as er:
        await msg.edit(f"__ОШИБКА: {er}__")
        LOGS.exception(er)


@ultroid_cmd("storydl")
async def downloadUserStories(event: NewMessage.Event):
    replied = await event.get_reply_message()
    message = await event.eor(get_string("com_1"))
    
    try:
        text_input = event.text.split(maxsplit=1)[1]
        # Проверяем, является ли ввод ссылкой на историю Telegram
        story_link_pattern = r"https?://t\.me/([^/]+)/s/(\d+)"
        match = re.match(story_link_pattern, text_input)
        
        if match:
            # Извлекаем юзернейм и ID истории из ссылки
            username = match.group(1)
            story_id = int(match.group(2))
            
            try:
                # Получаем сущность по юзернейму
                entity = await event.client.get_entity(username)
                
                # Используем GetStoriesByIDRequest для получения конкретной истории
                stories_response = await event.client(
                    GetStickerSetByIDRequest(
                        entity.id,
                        id=[story_id]
                    )
                )
                print(stories_response)
                
                if not stories_response.stories:
                    return await message.eor("ОШИБКА: История не найдена или истекла!")

                # Скачиваем и загружаем историю
                for story in stories_response.stories:
                    client: TelegramClient = event.client
                    file = await client.download_media(story.media)
                    caption = story.caption if hasattr(story, 'caption') else ""
                    await message.reply(
                        caption,
                        file=file
                    )
                    os.remove(file)
                
                return await message.eor("**История загружена!**", time=5)

            except Exception as er:
                await message.eor(f"ОШИБКА при получении истории: __{er}__")
                LOGS.exception(er)
                return
        
        # Если это не ссылка на историю, выполняем стандартную функциональность
        username = text_input
        
    except IndexError as er:
        LOGS.exception
        if replied and isinstance(replied.sender, User):
            username = replied.sender_id
        else:
            return await message.eor(
                "Ответьте на пользователя, укажите юзернейм или ссылку на историю!"
            )
            
    with suppress(ValueError):
        username = int(username)

    stories = None
    
    try:
        entity = await event.client.get_entity(username)
        if isinstance(entity, Channel):
            full_user: UserFull = (
                await event.client(GetFullChannelRequest(entity.id))
            ).full_channel
            stories = full_user.stories
        else:
            full_user: UserFull = (
                await event.client(GetFullUserRequest(id=username))
            ).full_user 
            stories = full_user.stories
    except Exception as er:
        await message.eor(f"ОШИБКА: __{er}__")
        return

    if not (stories and stories.stories):
        await message.eor("ОШИБКА: Истории не найдены!")
        return
    for story in stories.stories[:5]:
        client: TelegramClient = event.client
        file = await client.download_media(story.media)
        caption = story.caption if hasattr(story, 'caption') else ""
        await message.reply(
            caption,
            file=file
        )
        os.remove(file)

    await message.eor("**Истории загружены!**", time=5)
