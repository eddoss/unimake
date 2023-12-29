import os
from pathlib import Path
from textwrap import dedent

from beartype import beartype
from beartype.typing import Iterable
from pydantic import Field

from umk.framework.remote.interface import Interface
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell


class Compose(Interface):
    service: str = Field(
        default="",
        description="Target compose service"
    )
    file: Path = Field(
        default=Path(),
        description="Compose file path"
    )
    arguments: dict[str, str] = Field(
        default_factory=dict,
    )

    @beartype
    def __init__(
        self,
        name: str = "",
        description: str = "Existing docker-compose environment",
        default: bool = False,
        file: Path = Path(),
        service: str = "",
        shell: str = "sh",
        cmd: Iterable[str] = ("docker", "compose"),
    ):
        super().__init__(name=name, description=description, default=default)
        self._file = file.expanduser().resolve().absolute()
        self._service = service
        self._cmd = list(cmd)
        self._args = {}
        self._sh = shell
        self._details['shell'] = Property('shell', 'Default shell name', self.sh)
        self._details['command'] = Property('command', 'Docker compose command', self._cmd)
        self._details['service'] = Property('service', 'Default service name', self.service)
        self._details['file'] = Property('file', 'Path to compose file', self.service)
        self._details['arguments'] = Property('arguments', 'List of the build arguments', self.arguments)

    @beartype
    def build(self, *args, **kwargs):
        command = self.cmd.copy()
        command.extend(["build"])
        for k, v in self._args.items():
            command.extend(["--build-arg", f"{k}={v}"])
        Shell(command, name=self.name).sync()

    def destroy(self, *args, **kwargs):
        command = self.cmd
        command.extend(["down", "--remove-orphans", "--rmi", "all"])
        Shell(command, name=self.name).sync()

    @beartype
    def up(self, *args, **kwargs):
        command = self.cmd
        command.extend(["up", "--detach", "--no-recreate"])
        Shell(command, name=self.name).sync()

    def down(self, *args, **kwargs):
        command = self.cmd
        command.append("down")
        Shell(command, name=self.name).sync()

    @beartype
    def shell(self, *args, **kwargs):
        command = self.cmd
        command.extend(["exec", "-i", "-t", self._service, self.sh])
        Shell(command, name=self.name).sync()

    @beartype
    def execute(self, cmd: list[str], cwd: str = "", env: envs.Optional = None, *args, **kwargs):
        command = self.cmd
        command.extend(["exec", "-i", "-t"])
        if cwd:
            command.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                command.extend(["-e", f"{k}={v}"])
        command.append(self._service)
        command.extend(cmd)
        Shell(command, name=self.name).sync()

    @beartype
    def upload(self, paths: dict[str, str], *args, **kwargs):
        if not paths:
            return
        for src, dst in paths.items():
            Global.console.print(f"[bold]\[{self.name}] upload: {src} -> {dst}")
            cmd = self.cmd
            cmd.extend(['cp', src, f"{self.service}:{dst}"])
            Shell(command=cmd, name=self.name, log=False).sync()

    @beartype
    def download(self, paths: dict[str, str], *args, **kwargs):
        if not paths:
            return
        for src, dst in paths.items():
            Global.console.print(f"[bold]\[{self.name}] download: {src} -> {dst}")
            dst = Path(dst).expanduser().resolve().absolute()
            if not dst.parent.exists():
                os.makedirs(dst.parent)
            cmd = self.cmd
            cmd.extend(['cp', f"{self.service}:{src}", dst.as_posix()])
            Shell(command=cmd, name=self.name, log=False).sync()


class CustomCompose(Compose):
    @property
    def specification(self) -> str:
        return self._specification

    @specification.setter
    @beartype
    def specification(self, value: str):
        self._specification = dedent(value).lstrip()
        self._details['specification'].value = self.specification

    @beartype
    def __init__(
        self,
        name: str = "",
        description: str = "Custom docker-compose environment",
        default: bool = False,
        file: Path = Path(),
        service: str = "",
        shell: str = "sh",
        cmd: Iterable[str] = ("docker", "compose"),
    ):
        super().__init__(
            name=name,
            description=description,
            default=default,
            file=file,
            service=service,
            cmd=cmd,
            shell=shell
        )
        self._specification = ""
        self._details['specification'] = Property(
            'specification',
            'Compose specification',
            self.specification
        )

    @beartype
    def build(self, *args, **kwargs):
        with open(self._file, "w") as stream:
            stream.write(self.specification)
        super().build(*args, **kwargs)
