from beartype.typing import List, Union
from beartype import beartype
from pathlib import Path

Source = Union[str, Path]


class BuildFlags:
    @property
    def go(self) -> List[str]:
        return self._go

    @go.setter
    @beartype
    def go(self, value: List[str]):
        self._go = value

    @property
    def gc(self) -> List[str]:
        return self._gc

    @gc.setter
    @beartype
    def gc(self, value: List[str]):
        self._gc = value

    @property
    def ld(self) -> List[str]:
        return self._ld

    @ld.setter
    @beartype
    def ld(self, value: List[str]):
        self._ld = value

    def __init__(self):
        self._go: List[str] = []
        self._gc: List[str] = []
        self._ld: List[str] = []


class BuildArgs:
    @staticmethod
    @beartype
    def new(mode: str, output: Path = Path(), sources: List[Source] = None) -> 'BuildArgs':
        result = BuildArgs()
        result.output = output
        if sources:
            result.sources = sources
        if mode == "debug":
            result.flags.gc.append('all=-N')
            result.flags.gc.append('-l')
        elif mode == "release":
            result.flags.gc.append('-dwarf=false')
            result.flags.ld.append('-s')
            result.flags.ld.append('-w')

        return result

    @property
    def sources(self) -> List[Path]:
        return self._sources

    @sources.setter
    @beartype
    def sources(self, value: List[Path]):
        self._sources = value

    @property
    def output(self) -> Path:
        return self._output

    @output.setter
    @beartype
    def output(self, value: Path):
        self._output = value

    @property
    def flags(self) -> BuildFlags:
        return self._flags

    @flags.setter
    @beartype
    def flags(self, value: BuildFlags):
        self._flags = value

    def __init__(self):
        self._sources = []
        self._output = Path()
        self._flags = BuildFlags()

    def __str__(self) -> str:
        go = " ".join(self.flags.go)
        gc = f'{" ".join(self.flags.gc)}'
        ld = f'{" ".join(self.flags.ld)}'

        stringer = lambda p: Path(p).expanduser().resolve().absolute().as_posix()
        src = " ".join(map(stringer, self.sources))

        result = f'-o {self.output}'
        if self.flags.go:
            result += f' {go}'
        if self.flags.gc:
            result += f' -gcflags="{gc}"'
        if self.flags.ld:
            result += f' -ldflags="{ld}"'
        result += f' {src}'

        return result
