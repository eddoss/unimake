import abc
import asyncio
import subprocess
import sys
from asyncio import subprocess as async_subprocess
from beartype.typing import Union, Optional, Iterable
from beartype import beartype
from pathlib import Path
from umk.framework.system import environs as env
from umk.globals import Global


Command = Union[str, list[str]]


class Handler:
    @abc.abstractmethod
    def on_error(self, text: str): ...

    @abc.abstractmethod
    def on_output(self, text: str): ...


class Shell:
    @staticmethod
    def stringify(command: Iterable[str]) -> str:
        return " ".join(command)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        self._name = value

    @property
    def command(self) -> str:
        """
        Program and its arguments
        """
        return self._command

    @command.setter
    @beartype
    def command(self, value: Command):
        if issubclass(type(value), str):
            self._command = value.strip().split(" ")
        else:
            self._command = value

    @property
    def workdir(self) -> Path:
        """
        Path to working directory.
        """
        return self._workdir

    @workdir.setter
    @beartype
    def workdir(self, value: Path):
        self._workdir = value

    @property
    def environs(self) -> env.Environs:
        """
        Additional process environs (it will be merged to current envs and override).
        """
        return self._environs

    @environs.setter
    @beartype
    def environs(self, value: env.Optional):
        self._environs = env.Environs(inherit=True)
        if value:
            self._environs.update(value)

    @property
    def handler(self) -> Optional[Handler]:
        """
        Callbacks to handle output when pipe is used.
        """
        return self._handler

    @handler.setter
    @beartype
    def handler(self, value: Optional[Handler]):
        self._handler = value

    @property
    def log(self) -> bool:
        """
        Print executable command or not
        """
        return self._log

    @log.setter
    @beartype
    def log(self, value: bool):
        self._log = value

    devnull = subprocess.DEVNULL
    pipe = subprocess.PIPE
    stdout = sys.stdout
    stderr = sys.stderr

    @beartype
    def __init__(
        self,
        command: Command,
        workdir: Path = Global.paths.work,
        environs: env.Optional = None,
        handler: Optional[Handler] = None,
        name: str = "",
        log: bool = True,
    ):
        """
        Initialize shell attributes.

        :param command: Program and its arguments.
        :param workdir: Path to working directory.
        :param environs: Additional process environs (it will merge and override current envs).
        :param handler: Callbacks to handle output when pipe is used.
        :param name: Name of this shell instance.
        :param log: Print executable command or not.
        """
        self._name = name
        self._command = command
        self.command = command
        self._workdir = workdir
        self._environs = environs
        self._handler = handler
        self._log = log

    async def asyn(self, *, log: Optional[bool] = None) -> Optional[int]:
        cmd = self.stringify(self.command)
        self._log_cmd(log, cmd)
        inp, out, err = self._descriptors()
        prc: Optional[async_subprocess.Process] = None
        try:
            prc = await asyncio.create_subprocess_shell(
                cmd=cmd,
                stdin=inp,
                stdout=out,
                stderr=err,
                cwd=self.workdir,
                env=self.environs,
                shell=True
            )
        except Exception as e:
            self._on_exception(err, e)
            return

        if out != self.pipe and err != self.pipe:
            return await prc.wait()

        async def read(stream, func):
            while True:
                line = await stream.readline()
                if not line:
                    return
                func(self.handler, line.rstrip().decode("utf-8"))

        await asyncio.gather(
            read(prc.stdout, type(self.handler).on_output),
            read(prc.stderr, type(self.handler).on_error)
        )

        return await prc.wait()

    def sync(self, *, log: Optional[bool] = None) -> Optional[int]:
        cmd = self.stringify(self.command)
        self._log_cmd(log, cmd)
        prc: Optional[subprocess.Popen] = None
        inp, out, err = self._descriptors()

        try:
            prc = subprocess.Popen(
                args=self.command,
                # stdin=inp,
                stdout=out,
                stderr=err,
                universal_newlines=True,
                cwd=self.workdir,
                env=self.environs,
                shell=False
            )
        except Exception as e:
            self._on_exception(err, e)
            return

        if out != err != self.pipe:
            return prc.wait()

        while True:
            code = prc.poll()
            if code is not None:
                if prc.stdout:
                    for line in prc.stdout.readlines():
                        self.handler.on_output(line.rstrip())
                if prc.stderr:
                    for line in prc.stderr.readlines():
                        self.handler.on_error(line.rstrip())
                return code
            if prc.stdout:
                o = prc.stdout.readline()
                if o:
                    self.handler.on_output(o.rstrip())
            if prc.stderr:
                e = prc.stderr.readline()
                if e:
                    self.handler.on_error(e.strip())

    def _descriptors(self):
        inp = None
        out = self.stdout
        err = self.stderr
        if self.handler:
            ht = type(self.handler)
            if issubclass(ht, Devnull):
                out = self.devnull
                err = self.devnull
            else:
                out = self.pipe
                err = self.pipe
        return inp, out, err

    def _on_exception(self, err, e: Exception):
        if err == self.devnull:
            return
        elif err == self.stdout or err == self.stderr:
            print(e)
        elif err == self.pipe:
            self.handler.on_error(str(e))

    def _log_cmd(self, need: Optional[bool], cmd: str):
        need_log = need if need is not None else self.log
        if need_log:
            if self.name:
                Global.console.print(f"[bold]shell\['{self.name}']: {cmd}")
            else:
                Global.console.print(f"[bold]shell: {cmd}")


class Devnull(Handler):
    def on_error(self, text: str): ...

    def on_output(self, text: str): ...


class ColorPrinter(Handler):
    @property
    def out(self) -> str:
        return self._out

    @out.setter
    @beartype
    def out(self, value: str):
        self._out = value

    @property
    def err(self) -> str:
        return self._err

    @err.setter
    @beartype
    def err(self, value: str):
        self._err = value

    @beartype
    def __init__(self, out: str = ' ', err: str = '[error]'):
        """
        :param out: Output prefix.
        :param err: Error prefix.
        """
        self._out = out
        self._err = err

    def on_error(self, text: str):
        prefix = self.err
        if prefix.startswith('['):
            prefix = '\\' + prefix
        for line in text.split('\n'):
            if line.strip():
                Global.console.print(f'[bold red]{prefix}[/] [bold]{line}')

    def on_output(self, text: str):
        prefix = self.out
        if prefix.startswith('['):
            prefix = '\\' + prefix
        for line in text.split('\n'):
            if line.strip():
                Global.console.print(f'[bold green]{prefix}[/] [bold]{line}')
