from . import get_help

__doc__ = get_help("help_devtools")

import inspect
import sys
import traceback
from io import BytesIO, StringIO
from os import remove
from pprint import pprint

from telethon.utils import get_display_name

from pyUltroid import _ignore_eval

from . import *

# Используется для форматирования кода Eval, если установлен
try:
    import black
except ImportError:
    black = None
from random import choice

try:
    from yaml import safe_load
except ImportError:
    from pyUltroid.fns.tools import safe_load

from . import upload_file as uf
from telethon.tl import functions

fn = functions


@ultroid_cmd(
    pattern="sysinfo$",
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    if y and y.endswith("NOT_FOUND"):
        return await xx.edit(f"Ошибка: `{y}`")
    with open("neo.txt", "r", encoding="utf-8") as neo:
        p = (neo.read()).replace("\n\n", "")
    haa = await Carbon(code=p, file_name="neofetch", backgroundColor=choice(ATRA_COL))
    if isinstance(haa, dict):
        await xx.edit(f"`{haa}`")
    else:
        await e.reply(file=haa)
        await xx.delete()
    remove("neo.txt")


@ultroid_cmd(pattern="bash", fullsudo=True, only_devs=True)
async def _(event):
    carb, rayso, yamlf = None, None, False
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
        if cmd.split()[0] in ["-c", "--carbon"]:
            cmd = cmd.split(maxsplit=1)[1]
            carb = True
        if cmd.split()[0] in ["-r", "--rayso"]:
            cmd = cmd.split(maxsplit=1)[1]
            rayso = True
    except IndexError:
        return await event.eor(get_string("devs_1"), time=10)
    xx = await event.eor(get_string("com_1"))
    reply_to_id = event.reply_to_msg_id or event.id
    stdout, stderr = await bash(cmd, run_code=1)
    OUT = f"**☞ BASH\n\n• КОМАНДА:**\n`{cmd}` \n\n"
    err, out = "", ""
    if stderr:
        err = f"**• ОШИБКА:** \n`{stderr}`\n\n"
    if stdout:
        if (carb or udB.get_key("CARBON_ON_BASH")) and (
            event.is_private
            or event.chat.admin_rights
            or event.chat.creator
            or event.chat.default_banned_rights.embed_links
        ):
            li = await Carbon(
                code=stdout,
                file_name="bash",
                download=True,
                backgroundColor=choice(ATRA_COL),
            )
            if isinstance(li, dict):
                await xx.edit(
                    f"Неизвестный ответ от Carbon: `{li}`\n\nstdout`:{stdout}`\nstderr: `{stderr}`"
                )
                return
            url = uf(li)
            OUT = f"[\xad]({url}){OUT}"
            out = "**• ВЫВОД:**"
            remove(li)
        elif (rayso or udB.get_key("RAYSO_ON_BASH")) and (
            event.is_private
            or event.chat.admin_rights
            or event.chat.creator
            or event.chat.default_banned_rights.embed_links
        ):
            li = await Carbon(
                code=stdout,
                file_name="bash",
                download=True,
                backgroundColor=choice(ATRA_COL),
                rayso=True,
            )
            if isinstance(li, dict):
                await xx.edit(
                    f"Неизвестный ответ от Carbon: `{li}`\n\nstdout`:{stdout}`\nstderr: `{stderr}`"
                )
                return
            url = uf(li)
            OUT = f"[\xad]({url}){OUT}"
            out = "**• ВЫВОД:**"
            remove(li)
        else:
            if "pip" in cmd and all(":" in line for line in stdout.split("\n")):
                try:
                    load = safe_load(stdout)
                    stdout = ""
                    for data in list(load.keys()):
                        res = load[data] or ""
                        if res and "http" not in str(res):
                            res = f"`{res}`"
                        stdout += f"**{data}**  :  {res}\n"
                    yamlf = True
                except Exception as er:
                    stdout = f"`{stdout}`"
                    LOGS.exception(er)
            else:
                stdout = f"`{stdout}`"
            out = f"**• ВЫВОД:**\n{stdout}"
    if not stderr and not stdout:
        out = "**• ВЫВОД:**\n`Успешно`"
    OUT += err + out
    if len(OUT) > 4096:
        ultd = err + out
        with BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb=ULTConfig.thumb,
                allow_cache=False,
                caption=f"`{cmd}`" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )

            await xx.delete()
    else:
        await xx.edit(OUT, link_preview=not yamlf)


pp = pprint  # ignore: pylint
bot = ultroid = ultroid_bot


class u:
    _ = ""


def _parse_eval(value=None):
    if not value:
        return value
    if hasattr(value, "stringify"):
        try:
            return value.stringify()
        except TypeError:
            pass
    elif isinstance(value, dict):
        try:
            return json_parser(value, indent=1)
        except BaseException:
            pass
    elif isinstance(value, list):
        newlist = "["
        for index, child in enumerate(value):
            newlist += "\n  " + str(_parse_eval(child))
            if index < len(value) - 1:
                newlist += ","
        newlist += "\n]"
        return newlist
    return str(value)


@ultroid_cmd(pattern="eval", fullsudo=True, only_devs=True)
async def _(event):
    try:
        cmd = event.text.split(maxsplit=1)[1]
    except IndexError:
        return await event.eor(get_string("devs_2"), time=5)
    xx = None
    mode = ""
    spli = cmd.split()

    async def get_():
        try:
            cm = cmd.split(maxsplit=1)[1]
        except IndexError:
            await event.eor("->> Неверный формат <<-")
            cm = None
        return cm

    if spli[0] in ["-s", "--silent"]:
        await event.delete()
        mode = "silent"
    elif spli[0] in ["-n", "-noedit"]:
        mode = "no-edit"
        xx = await event.reply(get_string("com_1"))
    elif spli[0] in ["-gs", "--source"]:
        mode = "gsource"
    elif spli[0] in ["-ga", "--args"]:
        mode = "g-args"
    if mode:
        cmd = await get_()
    if not cmd:
        return
    if not mode == "silent" and not xx:
        xx = await event.eor(get_string("com_1"))
    if black:
        try:
            cmd = black.format_str(cmd, mode=black.Mode())
        except BaseException:
            # Считаем это ошибкой кода, переходим к её отображению далее.
            pass
    reply_to_id = event.reply_to_msg_id or event
    if any(item in cmd for item in KEEP_SAFE().All) and (
        not (event.out or event.sender_id == ultroid_bot.uid)
    ):
        warning = await event.forward_to(udB.get_key("LOG_CHANNEL"))
        await warning.reply(
            f"Подозрительная активность от {inline_mention(await event.get_sender())}"
        )
        _ignore_eval.append(event.sender_id)
        return await xx.edit(
            "`Подозрительная активность⚠️!\nСообщено владельцу. Запрос отклонён!`"
        )
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc, timeg = None, None, None, None
    tima = time.time()
    try:
        value = await aexec(cmd, event)
    except Exception:
        value = None
        exc = traceback.format_exc()
    tima = time.time() - tima
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if value:
        try:
            if mode == "gsource":
                exc = inspect.getsource(value)
            elif mode == "g-args":
                args = inspect.signature(value).parameters.values()
                name = ""
                if hasattr(value, "__name__"):
                    name = value.__name__
                exc = f"**{name}**\n\n" + "\n ".join([str(arg) for arg in args])
        except Exception:
            exc = traceback.format_exc()
    evaluation = exc or stderr or stdout or _parse_eval(value) or get_string("instu_4")
    if mode == "silent":
        if exc:
            msg = f"• <b>ОШИБКА EVAL\n\n• ЧАТ:</b> <code>{get_display_name(event.chat)}</code> [<code>{event.chat_id}</code>]"
            msg += f"\n\n∆ <b>КОД:</b>\n<code>{cmd}</code>\n\n∆ <b>ОШИБКА:</b>\n<code>{exc}</code>"
            log_chat = udB.get_key("LOG_CHANNEL")
            if len(msg) > 4000:
                with BytesIO(msg.encode()) as out_file:
                    out_file.name = "Eval-Error.txt"
                return await event.client.send_message(
                    log_chat, f"`{cmd}`", file=out_file
                )
            await event.client.send_message(log_chat, msg, parse_mode="html")
        return
    tmt = tima * 1000
    timef = time_formatter(tmt)
    timeform = timef if not timef == "0s" else f"{tmt:.3f}ms"
    final_output = "__►__ **EVAL** (__за {}__)\n```{}``` \n\n __►__ **ВЫВОД**: \n```{}``` \n".format(
        timeform,
        cmd,
        evaluation,
    )
    if len(final_output) > 4096:
        final_output = evaluation
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb=ULTConfig.thumb,
                allow_cache=False,
                caption=f"```{cmd}```" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )
        return await xx.delete()
    await xx.edit(final_output)


def _stringify(text=None, *args, **kwargs):
    if text:
        u._ = text
        text = _parse_eval(text)
    return print(text, *args, **kwargs)


async def aexec(code, event):
    # Создаём отдельное пространство имён для выполнения
    exec_globals = {
        'print': _stringify,
        'p': _stringify,
        'message': event,
        'event': event,
        'client': event.client,
        'reply': await event.get_reply_message(),
        'chat': event.chat_id,
        'u': u,
        '__builtins__': __builtins__,
        '__name__': __name__
    }
    
    # Формируем определение асинхронной функции
    wrapped_code = (
        'async def __aexec(e, client):\n' +
        '\n'.join(f'    {line}' for line in code.split('\n'))
    )
    
    try:
        # Выполняем обёрнутый код в нашем пространстве имён
        exec(wrapped_code, exec_globals)
        # Получаем определённую асинхронную функцию
        func = exec_globals['__aexec']
        # Выполняем её с нужными параметрами
        return await func(event, event.client)
    except Exception as e:
        raise Exception(f"Не удалось выполнить код: {str(e)}")


DUMMY_CPP = """#include <iostream>
using namespace std;

int main(){
!code
}
"""


@ultroid_cmd(pattern="cpp", only_devs=True)
async def doie(e):
    match = e.text.split(" ", maxsplit=1)
    try:
        match = match[1]
    except IndexError:
        return await e.eor(get_string("devs_3"))
    msg = await e.eor(get_string("com_1"))
    if "main(" not in match:
        new_m = "".join(" " * 4 + i + "\n" for i in match.split("\n"))
        match = DUMMY_CPP.replace("!code", new_m)
    open("cpp-ultroid.cpp", "w").write(match)
    m = await bash("g++ -o CppTeleFriend cpp-ultroid.cpp")
    o_cpp = f"• **Eval-Cpp**\n`{match}`"
    if m[1]:
        o_cpp += f"\n\n**• Ошибка :**\n`{m[1]}`"
        if len(o_cpp) > 3000:
            os.remove("cpp-ultroid.cpp")
            if os.path.exists("CppTeleFriend"):
                os.remove("CppTeleFriend")
            with BytesIO(str.encode(o_cpp)) as out_file:
                out_file.name = "error.txt"
                return await msg.reply(f"`{match}`", file=out_file)
        return await eor(msg, o_cpp)
    m = await bash("./CppTeleFriend")
    if m[0] != "":
        o_cpp += f"\n\n**• Вывод :**\n`{m[0]}`"
    if m[1]:
        o_cpp += f"\n\n**• Ошибка :**\n`{m[1]}`"
    if len(o_cpp) > 3000:
        with BytesIO(str.encode(o_cpp)) as out_file:
            out_file.name = "eval.txt"
            await msg.reply(f"`{match}`", file=out_file)
    else:
        await eor(msg, o_cpp)
    os.remove("CppTeleFriend")
    os.remove("cpp-ultroid.cpp")
