from beartype import beartype
from pathlib import Path
from umk.framework.adapters.delve.flags import Flags
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell
from umk.globals import Global


class Delve:
    @staticmethod
    @beartype
    def find():
        # TODO Implement search  algorithm
        return Delve(Path('/usr/bin/dlv'))

    @property
    def binary(self) -> Path:
        return self._binary

    @binary.setter
    @beartype
    def binary(self, value: Path):
        if not value.exists():
            raise FileNotFoundError(f"Invalid path to 'delve' binary: {value}")
        self._binary = value

    @property
    def flags(self) -> Flags:
        return self._flags

    @flags.setter
    @beartype
    def flags(self, value: Flags):
        self._flags = value

    @property
    def pwd(self) -> Path:
        return self._pwd

    @pwd.setter
    @beartype
    def pwd(self, value: Path):
        self._pwd = value

    @beartype
    def __init__(self, binary: Path, flags: Flags = Flags(2345), pwd: Path = Global.paths.work):
        self._binary = Path()
        self.binary = binary
        self._flags = flags
        self._pwd = pwd

    @beartype
    def attach(self, pid: int, exe: str = '', contin: bool = False, env: envs.Environs = None) -> Shell:
        cmd = f'{self.binary} {self.flags} attach {pid}'
        if exe.strip():
            cmd += f' {exe.strip()}'
        if contin:
            cmd += ' --continue'
        return Shell(
            command=cmd,
            workdir=self.pwd,
            environs=env
        )

    @beartype
    def exec(self, binary: Path, args: list[str] = None, contin: bool = False, tty: str = "", env: envs.Optional = None) -> Shell:
        cmd = f'{self.binary} {self.flags} exec'
        if tty:
            cmd += f' --tty={tty}'
        if contin:
            cmd += ' --continue'
        cmd += f' {Path(binary).expanduser().resolve().absolute().as_posix()}'
        if args:
            cmd += ' -- ' + ' '.join(args)
        return Shell(
            command=cmd,
            workdir=self.pwd,
            environs=env
        )
