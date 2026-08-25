from asyncio import create_subprocess_exec, subprocess


class Terminal:
    """
    Класс для асинхронного выполнения терминальных команд.

    Методы:

        run(commands: str)
            commands: Терминальные команды.
            Возвращает ID процесса (int)

        terminate(pid: int)
            pid: ID процесса, возвращённый в методе `run`.
            Возвращает True, если завершён, иначе False (bool)

        output(pid: int)
            pid: ID процесса, возвращённый в методе `run`.
            Возвращает вывод процесса (str)

        error(pid: int)
            pid: ID процесса, возвращённый в методе `run`.
            Возвращает ошибку процесса (str)
    """

    def __init__(self) -> None:
        self._processes = {}

    @staticmethod
    def _to_str(data: bytes) -> str:
        return data.decode("utf-8").strip()

    async def run(self, *args) -> int:
        process = await create_subprocess_exec(
            *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        pid = process.pid
        self._processes[pid] = process
        return pid

    def terminate(self, pid: int) -> bool:
        try:
            self._processes.pop(pid)
            self._processes[pid].kill()
            return True
        except KeyError:
            return False

    async def output(self, pid: int) -> str:
        output = []
        while True:
            out = self._to_str(await self._processes[pid].stdout.readline())
            if not out:
                break
            output.append(out)
        return "\n".join(output)

    async def error(self, pid: int) -> str:
        error = []
        while True:
            err = self._to_str(await self._processes[pid].stderr.readline())
            if not err:
                break
            error.append(err)
        return "\n".join(error)

    @property
    def _auto_remove_processes(self) -> None:
        while self._processes:
            for proc in self._processes.keys():
                if proc.returncode is not None:  # процесс всё ещё работает
                    try:
                        self._processes.pop(proc)
                    except KeyError:
                        pass
