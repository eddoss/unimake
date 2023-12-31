from beartype import beartype
from beartype.typing import Optional
from pathlib import Path
from umk.framework.system import Environs
from umk.framework.system.shell import Shell
from umk.framework.adapters.go.build import BuildArgs
from umk.framework.adapters.go.mod import Mod


class Go:
    @staticmethod
    @beartype
    def find(version: str):
        # TODO Implement search  algorithm
        return Go(Path("/usr/bin/go"))

    @property
    def binary(self) -> Path:
        return self._binary

    @binary.setter
    @beartype
    def binary(self, value: Path):
        if not value.exists():
            raise FileNotFoundError(f"Invalid path to 'go' binary: {value}")
        self._binary = value
        self._mod = Mod(self._binary)

    @property
    def mod(self) -> Mod:
        return self._mod

    @beartype
    def __init__(self, binary: Path):
        self._binary = binary
        self._mod = Mod(self.binary)
        self.binary = binary

    @beartype
    def build(self, args: BuildArgs, env: Optional[Environs] = None) -> Shell:
        return Shell(
            command=f'{self.binary} build {args}',
            environs=env
        )
