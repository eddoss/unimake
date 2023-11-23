import os
from textwrap import dedent
from beartype import beartype
from beartype.typing import Iterable
from pathlib import Path
from umk.globals import Global
from umk.remote.interface import Interface, Property
from umk.system.environs import OptEnv
from umk.system.shell import Shell


class Container(Interface):
    @property
    def cmd(self) -> list[str]:
        return self._cmd

    @property
    def container(self) -> str:
        return self._container

    @container.setter
    @beartype
    def container(self, value: str):
        self._container = value
        self._details['container'].value = self._container

    @property
    def sh(self) -> str:
        return self._sh

    @sh.setter
    @beartype
    def sh(self, value: str):
        self._sh = value
        self._details['shell'].value = self._sh

    @beartype
    def __init__(
        self,
        name: str = "",
        description: str = "Docker container environment",
        default: bool = False,
        container: str = "",
        shell: str = "sh",
        cmd: str = "docker"
    ):
        super().__init__(name=name, default=default, description=description)
        self._container = container
        self._sh = shell
        self._cmd = [cmd]
        self._details['shell'] = Property('shell', 'Default shell name', self.sh)
        self._details['command'] = Property('command', 'Docker command', self.cmd)
        self._details['container'] = Property('container', 'Default container name', self.container)

    @beartype
    def shell(self, *args, **kwargs):
        command = self.cmd.copy()
        command.extend(["exec", "-i", "-t", self.container, self.sh])
        Shell(command, name=self.name).sync()

    @beartype
    def execute(self, cmd: list[str], cwd: str = "", env: OptEnv = None, *args, **kwargs):
        command = self._cmd.copy()
        command.extend(["exec", "-t"])
        if cwd:
            command.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                command.extend(["-e", f"{k}={v}"])
        command.append(self._container)
        command.extend(cmd)
        Shell(command, name=self.name).sync()

    @beartype
    def upload(self, paths: dict[str, str], *args, **kwargs):
        if not paths:
            return
        for src, dst in paths.items():
            Global.console.print(f"[bold]\[{self.name}] upload: {src} -> {dst}")
            cmd = self.cmd
            cmd.extend(['container', 'cp', '-q', src, f"{self.container}:{dst}"])
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
            cmd.extend(['container', 'cp', '-q', f"{self.container}:{src}", dst.as_posix()])
            Shell(command=cmd, name=self.name, log=False).sync()


class Compose(Interface):
    @property
    def cmd(self) -> list[str]:
        result = self._cmd.copy()
        result.extend(["--file", self._file.as_posix()])
        return result

    @property
    def service(self) -> str:
        return self._service

    @service.setter
    @beartype
    def service(self, value: str):
        self._service = value
        self._details['service'].value = self._service

    @property
    def file(self) -> Path:
        return self._file

    @file.setter
    @beartype
    def file(self, value: Path):
        self._file = value
        self._details['file'].value = self._file

    @property
    def arguments(self) -> dict[str, str]:
        return self._args

    @arguments.setter
    @beartype
    def arguments(self, value: dict[str, str]):
        self._args = value
        self._details['arguments'].value = self._args

    @property
    def sh(self) -> str:
        return self._sh

    @sh.setter
    @beartype
    def sh(self, value: str):
        self._sh = value
        self._details['shell'].value = self._sh

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
    def execute(self, cmd: list[str], cwd: str = "", env: OptEnv = None, *args, **kwargs):
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
