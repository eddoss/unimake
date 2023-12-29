import os
from umk import core
from umk.framework.filesystem import Path
from umk.framework.adapters.go.build import BuildArgs as GoBuildArgs


class Flags:
    class Log:
        @property
        def enabled(self) -> bool:
            return self._enabled

        @enabled.setter
        @core.typeguard
        def enabled(self, value: bool):
            self._enabled = value

        @property
        def dest(self) -> Path | None:
            return self._dest

        @dest.setter
        @core.typeguard
        def dest(self, value: Path | None):
            self._dest = value

        @property
        def out(self) -> Path | None:
            return self._out

        @out.setter
        @core.typeguard
        def out(self, value: Path | None):
            self._out = value

        def __init__(self, enabled: bool = False, dest: Path | None = None, out: Path | None = None):
            self._enabled: bool = enabled
            self._dest: Path | None = dest
            self._out: Path | None = out

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    @core.typeguard
    def port(self, value: int):
        self._port = value

    @property
    def log(self) -> Log:
        return self._log

    @log.setter
    @core.typeguard
    def log(self, value: Log):
        self._log = value

    @property
    def multiclient(self) -> bool:
        return self._multiclient

    @multiclient.setter
    @core.typeguard
    def multiclient(self, value: bool):
        self._multiclient = value

    @property
    def allow_non_terminal_interactive(self) -> bool:
        return self._allow_non_terminal_interactive

    @allow_non_terminal_interactive.setter
    @core.typeguard
    def allow_non_terminal_interactive(self, value: bool):
        self._allow_non_terminal_interactive = value

    @property
    def api(self) -> int:
        return self._api

    @api.setter
    @core.typeguard
    def api(self, value: int):
        self._api = value

    @property
    def backend(self) -> str:
        return self._backend

    @backend.setter
    @core.typeguard
    def backend(self, value: str):
        self._backend = value

    @property
    def headless(self) -> bool:
        return self._headless

    @headless.setter
    @core.typeguard
    def headless(self, value: bool):
        self._headless = value

    @property
    def build_args(self) -> GoBuildArgs | None:
        return self._build_args

    @build_args.setter
    @core.typeguard
    def build_args(self, value: GoBuildArgs | None):
        self._build_args = value

    @property
    def validate(self) -> bool:
        return self._validate

    @validate.setter
    @core.typeguard
    def validate(self, value: bool):
        self._validate = value

    @property
    def aslr(self) -> bool:
        return self._aslr

    @aslr.setter
    @core.typeguard
    def aslr(self, value: bool):
        self._aslr = value

    @property
    def init(self) -> Path | None:
        return self._init

    @init.setter
    @core.typeguard
    def init(self, value: Path | None):
        self._init = value

    @property
    def redirect(self) -> list[str]:
        return self._redirect

    @redirect.setter
    @core.typeguard
    def redirect(self, value: list[str]):
        self._redirect = value

    @property
    def cwd(self) -> Path | None:
        return self._cwd

    @cwd.setter
    @core.typeguard
    def cwd(self, value: Path | None):
        self._cwd = value

    @property
    def only_same_user(self) -> bool:
        return self._only_same_user

    @only_same_user.setter
    @core.typeguard
    def only_same_user(self, value: bool):
        self._only_same_user = value

    def __init__(self, port: 2345):
        self._port = port
        self._log = Flags.Log()
        self._multiclient: bool = False
        self._allow_non_terminal_interactive: bool = False
        self._api: int = 2
        self._backend: str = 'default'
        self._headless: bool = True
        self._build_args: GoBuildArgs | None = None
        self._validate: bool = True
        self._aslr: bool = False
        self._init: os.PathLike | None = None
        self._redirect: list[str] = []
        self._cwd: os.PathLike | None = None
        self._only_same_user: bool = False

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
        result += f' --only-same-user={"true" if self.only_same_user else "false"}'
        # if self.redirect:
        #     result += f' --redirect={" ".join(self.redirect)}'
        return result
