import os
import pathlib

from beartype import beartype
from umk.globals import Global
from umk.system.shell import Shell


class Mod:
    @beartype
    def __init__(self, binary: pathlib.Path):
        self.binary = binary

    @beartype
    def tidy(self, compat: str = "", pwd=Global.paths.work) -> Shell:
        cmd = f'{self.binary} mod tidy'
        cpt = compat.strip()
        if cpt:
            cmd += f' -compat={cpt}'
        return Shell(cmd=cmd, cwd=pwd)

    @beartype
    def vendor(self, outdir: os.PathLike = "", pwd=Global.paths.work):
        cmd = f'{self.binary} mod vendor'
        if outdir:
            out = pathlib.Path(outdir).expanduser().resolve().absolute()
            cmd += f' -o={out}'
        return Shell(
            command=cmd,
            workdir=pwd
        )
