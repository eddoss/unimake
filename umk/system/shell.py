import asyncio
import subprocess
from beartype.typing import Callable, List, Union, Any, Optional
from beartype import beartype

from pathlib import Path
from umk.system.environs import Environs
from umk.application.config import Global

Command = Union[str, List[str]]
Printer = Callable[[str], Any]


class Shell:
    @staticmethod
    @beartype
    def wait(
        cmd: Command,
        pwd: Path = Global.paths.root,
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
            cwd=pwd,
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
        pwd: Path = Global.paths.root,
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
            cwd=pwd,
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

    @beartype
    def __init__(
        self,
        cmd: Command,
        pwd: Path = Global.paths.root,
        env: Optional[Environs] = None,
        out: Printer = print,
        err: Printer = print
    ):
        self.cmd = cmd
        self.pwd = pwd
        self.env = env
        self.out = out
        self.err = err

    def sync(self) -> int:
        return Shell.wait(cmd=self.cmd, pwd=self.pwd, env=self.env, out=self.out, err=self.err)

    async def asyn(self) -> int:
        return await Shell.run(cmd=self.cmd, pwd=self.pwd, env=self.env, out=self.out, err=self.err)
