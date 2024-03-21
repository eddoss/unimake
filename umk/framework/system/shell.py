import abc
import asyncio
import subprocess
import sys
from asyncio import subprocess as async_subprocess
from pathlib import Path
from umk.core.typings import Callable

from umk import core
from umk.framework.system.environs import Environs

Command = str | list[str]


class Handler:
    @abc.abstractmethod
    def on_error(self, text: str): ...

    @abc.abstractmethod
    def on_output(self, text: str): ...

    @abc.abstractmethod
    def on_exception(self, exc: Exception): ...


class Devnull(Handler):
    def on_error(self, text: str): ...

    def on_output(self, text: str): ...

    def on_exception(self, exc: Exception): ...


class Colorful(Handler, core.Model):
    out: str = core.Field(default="[bold green]${msg}", description="Output pattern")
    err: str = core.Field(default="[bold red]${msg}", description="Error pattern")
    exc: str = core.Field(default="[bold red]${exc}", description="Error pattern")

    def on_error(self, text: str):
        for line in text.split('\n'):
            if line.strip():
                core.globals.console.print(self.out.replace("${msg}", line))

    def on_output(self, text: str):
        for line in text.split('\n'):
            if line.strip():
                core.globals.console.print(self.err.replace("${msg}", line))

    def on_exception(self, exc: Exception):
        core.globals.console.print(self.err.replace("${exc}", str(exc)))


class Fetch(Handler, core.Model):
    out: list[str] = core.Field(default_factory=list, description="Output buffer")
    err: list[str] = core.Field(default_factory=list, description="Error buffer")
    exc: None | Exception = core.Field(default=None, description="Exception object")

    def on_error(self, text: str):
        self.err.append(text)

    def on_output(self, text: str):
        self.out.append(text)

    def on_exception(self, exc: Exception):
        self.exc = exc

    def outstr(self, splitter="\n") -> str:
        return splitter.join(self.out)

    def errstr(self, splitter="\n") -> str:
        return splitter.join(self.err)

    def excstr(self) -> str:
        return str(self.exc) if self.exc else ""


class Std(Handler):
    def on_error(self, text: str): ...

    def on_output(self, text: str): ...

    def on_exception(self, exc: Exception):
        core.globals.log.error(msg=str(exc))


devnull = subprocess.DEVNULL
pipe = subprocess.PIPE
stdout = sys.stdout
stderr = sys.stderr


class Shell(core.Model):
    name: str = core.Field(
        default="",
        description="Shell name (just for convenience)"
    )
    cmd: list[str | Path] = core.Field(
        default_factory=list,
        description="Shell command and it's options"
    )
    workdir: None | Path | str = core.Field(
        default=None,
        description="Shell working directory"
    )
    environs: None | Environs = core.Field(
        default=None,
        description="Shell environment variables"
    )
    handler: None | Handler = core.Field(
        default_factory=Std,
        description="Result handler"
    )
    log: bool = core.Field(
        default=False,
        description="Print command or not"
    )
    stringifier: Callable[[list[str | Path]], str] = core.Field(
        default=lambda args: " ".join([str(entry) for entry in args]),
        description="List to string converter (it's need to convert command list to string)"
    )

    async def asyn(self, *, log: bool | None = None) -> int | None:
        cmd = self.stringifier(self.cmd)
        self._log_cmd(log, cmd)
        inp, out, err = self._descriptors()
        prc: async_subprocess.Process | None = None
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
            if self.handler:
                self.handler.on_exception(e)
            return

        if out != pipe and err != pipe:
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

    def sync(self, *, log: bool | None = None) -> int | None:
        self._log_cmd(log, self.stringifier(self.cmd))
        prc: subprocess.Popen | None = None
        inp, out, err = self._descriptors()

        try:
            prc = subprocess.Popen(
                args=self.cmd,
                stdout=out,
                stderr=err,
                universal_newlines=True,
                cwd=self.workdir,
                env=self.environs,
                shell=False
            )
        except Exception as e:
            self.handler.on_exception(e)
            return

        if out != err != pipe:
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
        out = stdout
        err = stderr
        if self.handler:
            t = type(self.handler)
            if issubclass(t, Devnull):
                out = devnull
                err = devnull
            elif issubclass(t, Std):
                out = stdout
                err = stderr
            else:
                out = pipe
                err = pipe
        return inp, out, err

    def _log_cmd(self, need: bool | None, cmd: str):
        need_log = need if need is not None else self.log
        if need_log:
            if self.name:
                core.globals.console.print(f"[bold]shell\['{self.name}']: {cmd}")
            else:
                core.globals.console.print(f"[bold]shell: {cmd}")
