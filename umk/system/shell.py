import asyncio
import subprocess
from beartype.typing import Callable, Union, Any, Optional
from beartype import beartype

from pathlib import Path
from umk.system.environs import Environs, OptEnv
from umk.globals import Global

Command = Union[str, list[str]]
Printer = Callable[[str], Any]


class Shell:
    @staticmethod
    @beartype
    def wait(
        cmd: Command,
        cwd: Path = Global.paths.work,
        env: Optional[Environs] = None,
        out: Printer = print,
        err: Printer = print
    ) -> int:
        args = cmd
        if isinstance(cmd, list):
            args = " ".join(cmd)
        print(cmd)
        e = Environs(inherit=True)
        if env:
            e.update(env)
        with subprocess.Popen(
            args=args,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            shell=True,
            env=e
        ) as proc:
            while proc.poll() is None:
                if proc.stdout:
                    line = proc.stdout.readline()
                    if out and line != "":
                        out(line.rstrip())
                if proc.stderr:
                    line = proc.stderr.readline()
                    if err and line != "":
                        err(line.rstrip())
            return proc.returncode

    @staticmethod
    @beartype
    async def run(
        cmd: Command,
        cwd: Path = Global.paths.work,
        env: Optional[Environs] = None,
        out: Printer = print,
        err: Printer = print
    ) -> int:
        args = cmd
        if isinstance(cmd, list):
            args = " ".join(cmd)
        print(cmd)
        e = Environs(inherit=True)
        if env:
            e.update(env)
        proc = await asyncio.create_subprocess_shell(
            cmd=args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=e
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            line = stdout.decode()
            if out and line != "":
                out(line.rstrip())
        if stderr:
            line = stderr.decode()
            if err and line != "":
                err(line.rstrip())

        return proc.returncode

    @property
    def cmd(self) -> str:
        return self._cmd

    @cmd.setter
    @beartype
    def cmd(self, value: Command):
        if issubclass(type(value), str):
            self._cmd = value
        elif issubclass(type(value), list):
            self._cmd = " ".join(value)

    @property
    def cwd(self) -> Path:
        return self._cwd

    @cwd.setter
    @beartype
    def cwd(self, value: Path):
        self._cwd = value

    @property
    def env(self) -> Environs:
        return self._env

    @env.setter
    @beartype
    def env(self, value: Environs):
        self._env = value

    @property
    def out(self) -> Printer:
        return self._out

    @out.setter
    @beartype
    def out(self, value: Printer):
        self._out = value

    @property
    def err(self) -> Printer:
        return self._err

    @err.setter
    @beartype
    def err(self, value: Printer):
        self._err = value

    @beartype
    def __init__(
        self,
        cmd: Command,
        cwd: Path = Global.paths.work,
        env: OptEnv = None,
        out: Printer = print,
        err: Printer = print
    ):
        self._cmd = cmd
        self.cmd = cmd
        self._cwd = cwd
        self._env = env
        self._out = out
        self._err = err

    def sync(self) -> int:
        return Shell.wait(cmd=self.cmd, cwd=self.cwd, env=self.env, out=self.out, err=self.err)

    async def asyn(self) -> int:
        return await Shell.run(cmd=self.cmd, cwd=self.cwd, env=self.env, out=self.out, err=self.err)
