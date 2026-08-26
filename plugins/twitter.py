"""
✘ Доступные команды -

• `{i}tw <текст твита>`
    Опубликовать текст как твит.

• `{i}twr <id/ссылка твита>`
    Получить детали твита с количеством ответов/цитат/комментариев.

• `{i}twuser <юзернейм>`
    Получить данные пользователя аккаунта Twitter.

• `{i}twl <ссылка на твит>`
    Загрузить медиа из твита в Telegram.

"""

import os
from twikit import Client
from . import LOGS, eor, get_string, udB, ultroid_cmd

# Храним клиент глобально
twitter_client = None

# Получаем путь к файлу cookies
COOKIES_FILE = "resources/auth/twitter_cookies.json"

async def get_client():
    global twitter_client
    if twitter_client:
        return twitter_client

    if not all(udB.get_key(key) for key in ["TWITTER_USERNAME", "TWITTER_EMAIL", "TWITTER_PASSWORD"]):
        raise Exception("Сначала задайте TWITTER_USERNAME, TWITTER_EMAIL и TWITTER_PASSWORD в vars!")

    # Создаём каталог авторизации, если он не существует
    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

    client = Client()
    await client.login(
        auth_info_1=udB.get_key("TWITTER_USERNAME"),
        auth_info_2=udB.get_key("TWITTER_EMAIL"),
        password=udB.get_key("TWITTER_PASSWORD"),
        cookies_file=COOKIES_FILE
    )
    twitter_client = client
    return client



@ultroid_cmd(pattern="tw( (.*)|$)")
async def tweet_cmd(event):
    """Опубликовать твит"""
    text = event.pattern_match.group(1).strip()
    if not text:
        return await event.eor("🚫 `Укажите текст для твита!`")

    msg = await event.eor("🕊 `Публикация твита...`")
    try:
        client = await get_client()
        tweet = await client.create_tweet(text=text)
        await msg.edit(f"✨ **Успешно опубликовано!**\n\n🔗 https://x.com/{tweet.user.screen_name}/status/{tweet.id}")
    except Exception as e:
        await msg.edit(f"❌ **Ошибка:**\n`{str(e)}`")


@ultroid_cmd(pattern="twdetail( (.*)|$)")
async def twitter_details(event):
    """Получить детали твита"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Укажите ID/ссылку твита, чтобы получить детали!`")

    msg = await event.eor("🔍 `Получение деталей твита...`")
    try:
        client = await get_client()
        from urllib.parse import urlparse
        parsed_url = urlparse(match)
        if parsed_url.hostname in ["twitter.com", "x.com"]:
            tweet_id = parsed_url.path.split("/")[-1].split("?")[0]
        else:
            tweet_id = match

        tweet = await client.get_tweet_by_id(tweet_id)
        text = "🐦 **Детали твита**\n\n"
        text += f"📝 **Содержимое:** `{tweet.text}`\n\n"
        if hasattr(tweet, "metrics"):
            text += f"❤️ **Лайки:** `{tweet.metrics.likes}`\n"
            text += f"🔄 **Ретвиты:** `{tweet.metrics.retweets}`\n"
            text += f"💬 **Ответы:** `{tweet.metrics.replies}`\n"
            text += f"👁 **Просмотры:** `{tweet.metrics.views}`\n"

        await msg.edit(text)
    except Exception as e:
        await msg.edit(f"❌ **Ошибка:**\n`{str(e)}`")


@ultroid_cmd(pattern="twuser( (.*)|$)")
async def twitter_user(event):
    """Получить данные пользователя"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Укажите юзернейм, чтобы получить детали!`")

    msg = await event.eor("🔍 `Получение данных пользователя...`")
    try:
        client = await get_client()
        user = await client.get_user_by_screen_name(match)
        text = "👤 **Данные пользователя Twitter**\n\n"
        text += f"📛 **Имя:** `{user.name}`\n"
        text += f"🔖 **Юзернейм:** `@{user.screen_name}`\n"
        text += f"📝 **Описание:** `{user.description}`\n\n"
        text += f"👥 **Подписчики:** `{user.followers_count}`\n"
        text += f"👣 **Подписки:** `{user.following_count}`\n"
        text += f"🐦 **Всего твитов:** `{user.statuses_count}`\n"
        text += f"📍 **Местоположение:** `{user.location or 'Не указано'}`\n"
        text += f"✅ **Подтверждён:** `{user.verified}`\n"

        if user.profile_image_url:
            image_url = user.profile_image_url.replace("_normal.", ".")
            await event.client.send_file(
                event.chat_id,
                file=image_url,
                caption=text,
                force_document=False
            )
            await msg.delete()
        else:
            await msg.edit(text)

    except Exception as e:
        await msg.edit(f"❌ **Ошибка:**\n`{str(e)}`")


@ultroid_cmd(pattern="twl( (.*)|$)")
async def twitter_media(event):
    """Скачать медиа из твита"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("🚫 `Укажите ссылку на твит, чтобы скачать медиа!`")

    msg = await event.eor("📥 `Загрузка медиа...`")
    try:
        client = await get_client()
        if "twitter.com" in match or "x.com" in match:
            tweet_id = match.split("/")[-1].split("?")[0]
        else:
            tweet_id = match

        tweet = await client.get_tweet_by_id(tweet_id)

        if not hasattr(tweet, "media"):
            return await msg.edit("😕 `В твите не найдено медиа!`")

        # Формируем подпись с текстом твита
        caption = f"🐦 **Твит от @{tweet.user.screen_name}**\n\n"
        caption += f"{tweet.text}\n\n"
        if hasattr(tweet, "metrics"):
            caption += f"❤️ `{tweet.metrics.likes}` 🔄 `{tweet.metrics.retweets}` 💬 `{tweet.metrics.replies}`"

        media_count = 0
        for media in tweet.media:
            if media.type == "photo":
                await event.client.send_file(
                    event.chat_id,
                    media.url,
                    caption=caption if media_count == 0 else None  # Добавляем подпись только к первому медиа
                )
                media_count += 1
            elif media.type == "video":
                if hasattr(media, "video_info") and isinstance(media.video_info, dict):
                    variants = media.video_info.get("variants", [])
                    mp4_variants = [
                        v for v in variants
                        if v.get("content_type") == "video/mp4" and "bitrate" in v
                    ]
                    if mp4_variants:
                        best_video = max(mp4_variants, key=lambda x: x["bitrate"])
                        video_caption = caption if media_count == 0 else ""  # Текст твита добавляем только к первому медиа
                        if video_caption:
                            video_caption += f"\n🎥 Качество видео: {best_video['bitrate']/1000:.0f}kbps"
                        else:
                            video_caption = f"🎥 Качество видео: {best_video['bitrate']/1000:.0f}kbps"

                        await event.client.send_file(
                            event.chat_id,
                            best_video["url"],
                            caption=video_caption
                        )
                        media_count += 1

        if media_count > 0:
            await msg.edit(f"✅ Успешно загружено медиа: {media_count}!")
            await msg.delete()
        else:
            await msg.edit("😕 `Не удалось загрузить медиа!`")
    except Exception as e:
        await msg.edit(f"❌ **Ошибка:**\n`{str(e)}`")
