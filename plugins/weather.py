# Ultroid ~ UserBot
# Copyright (C) 2023-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
**Получение данных о погоде через OpenWeatherMap API**
❍  Доступные команды -

• `{i}weather` <название города>
    Показывает погоду в городах

• `{i}air` <название города>
    Показывает состояние воздуха в городах
"""

import datetime
import time
from datetime import timedelta

import aiohttp
import pytz

from . import async_searcher, get_string, udB, ultroid_cmd


async def get_timezone(offset_seconds, use_utc=False):
    offset = timedelta(seconds=offset_seconds)
    hours, remainder = divmod(offset.seconds, 3600)
    sign = "+" if offset.total_seconds() >= 0 else "-"
    timezone = "UTC" if use_utc else "GMT"
    if use_utc:
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            now = datetime.datetime.now(tz)
            if now.utcoffset() == offset:
                return f"{m} ({timezone}{sign}{hours:02d})"
    else:
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            if m.startswith("Australia/"):
                now = datetime.datetime.now(tz)
                if now.utcoffset() == offset:
                    return f"{m} ({timezone}{sign}{hours:02d})"
        for m in pytz.all_timezones:
            tz = pytz.timezone(m)
            now = datetime.datetime.now(tz)
            if now.utcoffset() == offset:
                return f"{m} ({timezone}{sign}{hours:02d})"
        return "Часовой пояс не найден"

async def getWindinfo(speed: str, degree: str) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    ix = round(degree / (360.00 / len(dirs)))
    kmph = str(float(speed) * 3.6) + " km/h"
    return f"[{dirs[ix % len(dirs)]}] {kmph}"

async def get_air_pollution_data(latitude, longitude, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if "list" in data:
                air_pollution = data["list"][0]
                return air_pollution
            else:
                return None


@ultroid_cmd(pattern="weather ?(.*)")
async def weather(event):
    if event.fwd_from:
        return
    msg = await event.eor(get_string("com_1"))
    x = udB.get_key("OPENWEATHER_API")
    if x is None:
        await event.eor(
            "API не найден. Получите его [здесь](https://api.openweathermap.org)\nИ добавьте в ключ Redis OPENWEATHER_API",
            time=8,
        )
        return
    input_str = event.pattern_match.group(1)
    if not input_str:
        await event.eor("Местоположение не указано...", time=5)
        return
    elif input_str == "butler":
        await event.eor("ищите butler,au для australila", time=5)
    sample_url = f"https://api.openweathermap.org/data/2.5/weather?q={input_str}&APPID={x}&units=metric"
    try:
        response_api = await async_searcher(sample_url, re_json=True)
        if response_api["cod"] == 200:
            country_time_zone = int(response_api["timezone"])
            tz = f"{await get_timezone(country_time_zone)}"
            sun_rise_time = int(response_api["sys"]["sunrise"]) + country_time_zone
            sun_set_time = int(response_api["sys"]["sunset"]) + country_time_zone
            await msg.edit(
                f"{response_api['name']}, {response_api['sys']['country']}\n\n"
                f"╭────────────────•\n"
                f"╰➢ **Погода:** {response_api['weather'][0]['description']}\n"
                f"╰➢ **Часовой пояс:** {tz}\n"
                f"╰➢ **Восход:** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_rise_time))}\n"
                f"╰➢ **Закат:** {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(sun_set_time))}\n"
                f"╰➢ **Ветер:** {await getWindinfo(response_api['wind']['speed'], response_api['wind']['deg'])}\n"
                f"╰➢ **Температура:** {response_api['main']['temp']}°C\n"
                f"╰➢ **Ощущается как:** {response_api['main']['feels_like']}°C\n"
                f"╰➢ **Минимум:** {response_api['main']['temp_min']}°C\n"
                f"╰➢ **Максимум:** {response_api['main']['temp_max']}°C\n"
                f"╰➢ **Давление:** {response_api['main']['pressure']} hPa\n"
                f"╰➢ **Влажность:** {response_api['main']['humidity']}%\n"
                f"╰➢ **Видимость:** {response_api['visibility']} m\n"
                f"╰➢ **Облачность:** {response_api['clouds']['all']}%\n"
                f"╰────────────────•\n\n"
            )
        else:
            await msg.edit(response_api["message"])
    except Exception as e:
        await event.eor(f"Произошла непредвиденная ошибка: {str(e)}", time=5)


@ultroid_cmd(pattern="air ?(.*)")
async def air_pollution(event):
    if event.fwd_from:
        return
    msg = await event.eor(get_string("com_1"))
    x = udB.get_key("OPENWEATHER_API")
    if x is None:
        await event.eor(
            "API не найден. Получите его [здесь](https://api.openweathermap.org)\nИ добавьте в ключ Redis OPENWEATHER_API",
            time=8,
        )
        return
    input_str = event.pattern_match.group(1)
    if not input_str:
        await event.eor("`Местоположение не указано...`", time=5)
        return
    if input_str.lower() == "perth":
        geo_url = f"https://geocode.xyz/perth%20au?json=1"
    else:
        geo_url = f"https://geocode.xyz/{input_str}?json=1"
    geo_data = await async_searcher(geo_url, re_json=True)
    try:
        longitude = geo_data["longt"]
        latitude = geo_data["latt"]
    except KeyError as e:
        LOGS.info(e)
        await event.eor("`Не удалось найти координаты для указанного местоположения.`", time=5)
        return
    try:
        city = geo_data["standard"]["city"]
        prov = geo_data["standard"]["prov"]
    except KeyError as e:
        LOGS.info(e)
        await event.eor("`Не удалось найти город для указанных координат.`", time=5)
        return
    air_pollution_data = await get_air_pollution_data(latitude, longitude, x)
    if air_pollution_data is None:
        await event.eor(
            "`Не удалось получить данные о загрязнении воздуха для указанного местоположения.`", time=5
        )
        return
    await msg.edit(
        f"{city}, {prov}\n\n"
        f"╭────────────────•\n"
        f"╰➢ **ИКВ:** {air_pollution_data['main']['aqi']}\n"
        f"╰➢ **Оксид углерода:** {air_pollution_data['components']['co']}µg/m³\n"
        f"╰➢ **Оксид азота:** {air_pollution_data['components']['no']}µg/m³\n"
        f"╰➢ **Диоксид азота:** {air_pollution_data['components']['no2']}µg/m³\n"
        f"╰➢ **Озон:** {air_pollution_data['components']['o3']}µg/m³\n"
        f"╰➢ **Диоксид серы:** {air_pollution_data['components']['so2']}µg/m³\n"
        f"╰➢ **Аммиак:** {air_pollution_data['components']['nh3']}µg/m³\n"
        f"╰➢ **Мелкие частицы (PM₂.₅):** {air_pollution_data['components']['pm2_5']}\n"
        f"╰➢ **Крупные частицы (PM₁₀):** {air_pollution_data['components']['pm10']}\n"
        f"╰────────────────•\n\n"
    )
