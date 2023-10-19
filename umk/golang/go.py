import os
import pathlib

from beartype import beartype
from beartype.typing import Optional

from umk import exceptions
from umk.system.environs import Environs
from umk.system.shell import Shell
from umk.golang.build import BuildArgs
from umk.golang.mod import Mod


class Go:
    @staticmethod
    @beartype
    def find(version: str):
        # TODO Implement search  algorithm
        return Go(pathlib.Path("/usr/bin/go"))

    @beartype
    def __init__(self, binary: os.PathLike):
        self.binary = pathlib.Path(binary)
        if not self.binary.exists():
            raise exceptions.GoBinaryExistsError(f"Invalid path to 'go' binary: {self.binary}")
        self.mod = Mod(self.binary)

    @beartype
    def build(self, args: BuildArgs, env: Optional[Environs] = None) -> Shell:
        return Shell(cmd=f'{self.binary} build {args}', env=env)
