# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# Этот файл является частью < https://github.com/TeamUltroid/Ultroid/ >
# Пожалуйста, прочитайте GNU Affero General Public License в
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

"""
Исключения, которые могут быть вызваны самим py-Ultroid.
"""


class pyUltroidError(Exception):
    ...


class DependencyMissingError(ImportError):
    ...


class RunningAsFunctionLibError(pyUltroidError):
    ...
