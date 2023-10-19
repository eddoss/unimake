import os
from beartype.typing import Dict
from beartype import beartype


@beartype
def prepend(envs: Dict[str, str], name: str, *values: str) -> None:
    nonempty = filter(None, values)
    value = os.pathsep.join(nonempty)
    if name in envs and envs[name]:
        value += os.pathsep + envs[name]
    envs[name] = value


@beartype
def append(envs: Dict[str, str], name: str, *values: str) -> None:
    nonempty = filter(None, values)
    appended = os.pathsep.join(nonempty)
    if name in envs and envs[name]:
        appended = f'{envs[name]}{os.pathsep}{appended}'
    envs[name] = appended


class Environs(dict):
    @beartype
    def __init__(self, inherit=True):
        super().__init__()
        if inherit:
            for name, value in os.environ.items():
                self[name] = value

    @beartype
    def prepend(self, name: str, *values: str) -> None:
        prepend(self, name, *values)

    @beartype
    def append(self, name: str, *values: str) -> None:
        append(self, name, *values)
