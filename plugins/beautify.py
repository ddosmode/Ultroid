# Ultroid - ЮзерБот
# Авторские права (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочтите GNU Affero General Public License по адресу
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import get_help

__doc__ = get_help("help_beautify")


import os
import random

from telethon.utils import get_display_name
from urllib.parse import urlencode
from . import Carbon, ultroid_cmd, get_string, inline_mention
from secrets import token_hex

_colorspath = "resources/colorlist.txt"

if os.path.exists(_colorspath):
    with open(_colorspath, "r") as f:
        all_col = f.read().split()
else:
    all_col = []


@ultroid_cmd(
    pattern="(rc|c)arbon",
)
async def cr_bn(event):
    xxxx = await event.eor(get_string("com_1"))
    te = event.pattern_match.group(1)
    col = random.choice(all_col) if te[0] == "r" else "White"
    if event.reply_to_msg_id:
        temp = await event.get_reply_message()
        if temp.media:
            b = await event.client.download_media(temp)
            with open(b) as a:
                code = a.read()
            os.remove(b)
        else:
            code = temp.message
    else:
        try:
            code = event.text.split(" ", maxsplit=1)[1]
        except IndexError:
            return await xxxx.eor(get_string("carbon_2"))
    xx = await Carbon(code=code, file_name="ultroid_carbon", backgroundColor=col)
    if isinstance(xx, dict):
        await xxxx.edit(f"`{xx}`")
        return
    await xxxx.delete()
    await event.reply(
        f"Карбонизировано пользователем {inline_mention(event.sender)}",
        file=xx,
    )


@ultroid_cmd(
    pattern="ccarbon( (.*)|$)",
)
async def crbn(event):
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor(get_string("carbon_3"))
    msg = await event.eor(get_string("com_1"))
    if event.reply_to_msg_id:
        temp = await event.get_reply_message()
        if temp.media:
            b = await event.client.download_media(temp)
            with open(b) as a:
                code = a.read()
            os.remove(b)
        else:
            code = temp.message
    else:
        try:
            match = match.split(" ", maxsplit=1)
            code = match[1]
            match = match[0]
        except IndexError:
            return await msg.eor(get_string("carbon_2"))
    xx = await Carbon(code=code, backgroundColor=match)
    await msg.delete()
    await event.reply(
        f"Карбонизировано пользователем {inline_mention(event.sender)}",
        file=xx,
    )


RaySoTheme = [
    "meadow",
    "breeze",
    "raindrop",
    "candy",
    "crimson",
    "falcon",
    "sunset",
    "noir",
    "midnight",
    "bitmap",
    "ice",
    "sand",
    "forest",
    "mono",
]


@ultroid_cmd(pattern="rayso")
async def pass_on(ult):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        await ult.eor(
            "`playwright` не установлен!\nПожалуйста, установите его для использования этой команды.."
        )
        return

    proc = await ult.eor(get_string("com_1"))
    spli = ult.text.split()
    theme, dark, title, text = None, True, get_display_name(ult.chat), None
    if len(spli) > 1:
        if spli[1] in RaySoTheme:
            theme = spli[1]
            if len(spli) > 2:
                text = " ".join(spli[2:])
        else:
            text = " ".join(spli[1:])
    if ult.is_reply:
        try:
            msg = await ult.get_reply_message()
            text = msg.message if not text else text
            title = get_display_name(msg.sender)
            if not theme and spli[1] in RaySoTheme:
                theme = spli[1]
        except Exception as sam:
            LOGS.exception(sam)
    if not text:
        await proc.eor("Нет текста для украшения!")
        return
    if not theme:
        theme = random.choice(RaySoTheme)
    cleaned_text = "\n".join([line.strip() for line in text.splitlines()])
    name = token_hex(8) + ".png"
    data = {"darkMode": dark, "theme": theme, "title": title}
    url = f"https://ray.so/#{urlencode(data)}"
    async with async_playwright() as play:
        try:
            browser = await play.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            try:
                await page.wait_for_selector(
                    "div[class*='Editor_editor__']", timeout=60000
                )
                editor = await page.query_selector("div[class*='Editor_editor__']")
                await editor.focus()
                await editor.click()

                for line in cleaned_text.split("\n"):
                    await page.keyboard.type(line)
                    await page.keyboard.press("Enter")

                await page.evaluate(
                    """() => {
                    const button = document.querySelector('button[aria-label="Export as PNG"]');
                    button.click();
                }"""
                )

                async with page.expect_download() as download_info:
                    download = await download_info.value
                    await download.save_as(name)
            except playwright._impl._errors.TimeoutError:
                LOGS.error("Ошибка таймаута: Селектор не найден в течение 60 секунд.")
                await proc.eor("Не удалось найти редактор в течение 60 секунд.")
                return
        except Exception as e:
            LOGS.error(f"Произошла ошибка при работе playwright: {e}")
            await proc.eor("Произошла ошибка во время операции.")
            return
        finally:
            if os.path.exists(name):
                try:
                    await ult.reply(file=name)
                    await proc.try_delete()
                    os.remove(name)
                except Exception as e:
                    LOGS.error(f"Произошла ошибка при ответе с файлом: {e}")
                    await proc.eor("Не удалось отправить файл.")
            else:
                LOGS.error(f"Ошибка: Файл {name} не найден или недоступен.")
                await proc.eor("Не удалось сохранить файл.")
