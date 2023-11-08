import os
from beartype import beartype
from beartype.typing import Iterable
from pathlib import Path
from umk.globals import Global
from umk.remote.interface import Interface
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

    @property
    def sh(self) -> str:
        return self._sh

    @sh.setter
    @beartype
    def sh(self, value: str):
        self._sh = value

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

    def build(self, *args, **kwargs):
        Global.console.print(
            f"[bold]The '{self.name}' remote environment has no 'build' function.\n"
            f"[bold]It`s '{self.name}' remote environment has no 'build' function.\n"
        )

    def destroy(self, *args, **kwargs):
        Global.console.print(
            f"[bold]The '{self.name}' remote environment has no 'destroy' function"
        )

    def up(self, *args, **kwargs):
        Global.console.print(
            f"[bold]The '{self.name}' remote environment has no 'build' function"
        )

    def down(self, *args, **kwargs):
        ...

    @beartype
    def shell(self, *args, **kwargs):
        command = self.cmd.copy()
        command.extend(["exec", "-i", "-t", self.container, self.sh])
        # sh = Shell(command)
        # sh.sync()
        # TODO Fix shell routine and use sh.sync() instead of os.system()
        os.system(Shell(command).cmd)

    @beartype
    def execute(self, cmd: list[str], cwd: str = "", env: OptEnv = None):
        command = self._cmd.copy()
        command.extend(["exec", "-t"])
        if cwd:
            command.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                command.extend(["-e", f"{k}={v}"])
        command.append(self._container)
        command.extend(cmd)
        Shell.wait(command)


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

    @property
    def file(self) -> Path:
        return self._file

    @file.setter
    @beartype
    def file(self, value: Path):
        self._file = value

    @property
    def arguments(self) -> dict[str, str]:
        return self._args

    @arguments.setter
    @beartype
    def arguments(self, value: dict[str, str]):
        self._args = value

    @property
    def sh(self) -> str:
        return self._sh

    @sh.setter
    @beartype
    def sh(self, value: str):
        self._sh = value

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

    @beartype
    def build(self, *args, **kwargs):
        command = self.cmd.copy()
        command.extend(["build"])
        for k, v in self._args.items():
            command.extend(["--build-arg", f"{k}={v}"])
        Shell.wait(cmd=command)

    def destroy(self, *args, **kwargs):
        command = self.cmd
        command.extend(["rm", "-f", "-s", "-v"])
        Shell.wait(command)

    @beartype
    def up(self, *args, **kwargs):
        command = self.cmd
        command.extend(["up", "--detach", "--no-recreate"])
        Shell.wait(cmd=command)

    def down(self, *args, **kwargs):
        command = self.cmd
        command.append("down")
        Shell.wait(command)

    @beartype
    def shell(self, shell: str = "sh", *args, **kwargs):
        command = self.cmd
        command.extend(["exec", "-i", "-t", self._service, shell])
        # sh = Shell(command)
        # sh.sync()
        # TODO Fix shell routine and use sh.sync() instead of os.system()
        os.system(Shell(command).cmd)

    @beartype
    def execute(self, cmd: list[str], cwd: str = "", env: OptEnv = None):
        command = self.cmd
        command.extend(["exec", "-i", "-t"])
        if cwd:
            command.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                command.extend(["-e", f"{k}={v}"])
        command.append(self._service)
        command.extend(cmd)
        Shell.wait(command)


class CustomCompose(Compose):
    @property
    def specification(self) -> str:
        return self._specification

    @specification.setter
    @beartype
    def specification(self, value: str):
        self._specification = value

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

    @beartype
    def build(self, *args, **kwargs):
        with open(self._file, "w") as stream:
            stream.write(self.specification)
        super().build(*args, **kwargs)
