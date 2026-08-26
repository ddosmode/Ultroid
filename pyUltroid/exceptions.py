"""
Исключения, которые могут быть вызваны самим py-TeleFriend.
"""


class pyUltroidError(Exception):
    ...


class DependencyMissingError(ImportError):
    ...


class RunningAsFunctionLibError(pyUltroidError):
    ...
