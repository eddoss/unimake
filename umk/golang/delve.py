import os
import pathlib
from beartype.typing import Optional, List

from beartype import beartype

from umk import exceptions
from pathlib import Path
from umk.golang.build import BuildArgs as GoBuildArgs
from umk.system.shell import Shell
from umk.application.config import Global
from umk.system.environs import Environs


class GlobalFlags:
    class Log:
        @property
        def enabled(self) -> bool:
            return self._enabled

        @enabled.setter
        @beartype
        def enabled(self, value: bool):
            self._enabled = value

        @property
        def dest(self) -> Optional[Path]:
            return self._dest

        @dest.setter
        @beartype
        def dest(self, value: Optional[Path]):
            self._dest = value

        @property
        def out(self) -> Optional[Path]:
            return self._out

        @out.setter
        @beartype
        def out(self, value: Optional[Path]):
            self._out = value

        def __init__(self, enabled: bool = False, dest: Optional[Path] = None, out: Optional[Path] = None):
            self._enabled: bool = enabled
            self._dest: Optional[Path] = dest
            self._out: Optional[Path] = out

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    @beartype
    def port(self, value: int):
        self._port = value

    @property
    def log(self) -> Log:
        return self._log

    @log.setter
    @beartype
    def log(self, value: Log):
        self._log = value

    @property
    def multiclient(self) -> bool:
        return self._multiclient

    @multiclient.setter
    @beartype
    def multiclient(self, value: bool):
        self._multiclient = value

    @property
    def allow_non_terminal_interactive(self) -> bool:
        return self._allow_non_terminal_interactive

    @allow_non_terminal_interactive.setter
    @beartype
    def allow_non_terminal_interactive(self, value: bool):
        self._allow_non_terminal_interactive = value

    @property
    def api(self) -> int:
        return self._api

    @api.setter
    @beartype
    def api(self, value: int):
        self._api = value

    @property
    def backend(self) -> str:
        return self._backend

    @backend.setter
    @beartype
    def backend(self, value: str):
        self._backend = value

    @property
    def headless(self) -> bool:
        return self._headless

    @headless.setter
    @beartype
    def headless(self, value: bool):
        self._headless = value

    @property
    def build_args(self) -> Optional[GoBuildArgs]:
        return self._build_args

    @build_args.setter
    @beartype
    def build_args(self, value: Optional[GoBuildArgs]):
        self._build_args = value

    @property
    def validate(self) -> bool:
        return self._validate

    @validate.setter
    @beartype
    def validate(self, value: bool):
        self._validate = value

    @property
    def aslr(self) -> bool:
        return self._aslr

    @aslr.setter
    @beartype
    def aslr(self, value: bool):
        self._aslr = value

    @property
    def init(self) -> Optional[Path]:
        return self._init

    @init.setter
    @beartype
    def init(self, value: Optional[Path]):
        self._init = value

    @property
    def redirect(self) -> List[str]:
        return self._redirect

    @redirect.setter
    @beartype
    def redirect(self, value: List[str]):
        self._redirect = value

    @property
    def cwd(self) -> Optional[Path]:
        return self._cwd

    @cwd.setter
    @beartype
    def cwd(self, value: Optional[Path]):
        self._cwd = value

    def __init__(self, port: 2345):
        self._port = port
        self._log = GlobalFlags.Log()
        self._multiclient: bool = False
        self._allow_non_terminal_interactive: bool = False
        self._api: int = 2
        self._backend: str = 'default'
        self._headless: bool = True
        self._build_args: Optional[GoBuildArgs] = None
        self._validate: bool = True
        self._aslr: bool = False
        self._init: Optional[os.PathLike] = None
        self._redirect: List[str] = []
        self._cwd: Optional[os.PathLike] = None

    def __str__(self) -> str:
        result = f'--api-version={self.api} --listen=:{self.port}'
        if self.multiclient:
            result += ' --accept-multiclient'
        if self.allow_non_terminal_interactive:
            result += ' --allow-non-terminal-interactive'
        if self.headless:
            result += ' --headless=true'
        if self.backend:
            result += f' --backend={self.backend}'
        if self.build_args:
            result += f' --build-flags={self.build_args}'
        if self.validate:
            result += ' --check-go-version'
        if self.aslr:
            result += ' --disable-aslr'
        if self.init:
            result += f' --init={self.init}'
        if self.log.enabled:
            result += f' --log'
        if self.log.dest:
            result += f' --log-dest={self.log.dest}'
        if self.log.out:
            result += f' --log-output={self.log.out}'
        if self.cwd:
            result += f' --wd={self.cwd}'
        # if self.redirect:
        #     result += f' --redirect={" ".join(self.redirect)}'
        return result


class Delve:
    @staticmethod
    @beartype
    def find():
        # TODO Implement search  algorithm
        return Delve(Path('/usr/bin/dlv'))

    def __init__(self, binary: Path):
        self.binary = pathlib.Path(binary)
        if not self.binary.exists():
            raise exceptions.DelveBinaryExistsError(f"Invalid path to 'delve' binary: {self.binary}")

    @beartype
    def exec(
        self,
        binary: Path,
        bin_args: List[str] = None,
        contin=False,
        tty="",
        flags=GlobalFlags(2345),
        pwd=Global.paths.root,
        env: Environs = None
    ) -> Shell:
        res = Shell(f'{self.binary} {flags} exec', pwd=pwd, env=env)
        if tty:
            res.cmd += f' --tty={tty}'
        if contin:
            res.cmd += ' --continue'
        res.cmd += f' {pathlib.Path(binary).expanduser().resolve().absolute().as_posix()}'
        if bin_args:
            res.cmd += ' -- '
            res.cmd += ' '.join(bin_args)
        return res
