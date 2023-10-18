import os
import pathlib

from beartype import beartype

from umk.application.config import Global
from umk.system.shell import Shell


class Mod:
    @beartype
    def __init__(self, binary: pathlib.Path):
        self.binary = binary

    @beartype
    def tidy(self, compat: str = "", pwd=Global.paths.root) -> Shell:
        cmd = f'{self.binary} mod tidy'
        cpt = compat.strip()
        if cpt:
            cmd += f' -compat={cpt}'
        return Shell(cmd=cmd, pwd=pwd)

    @beartype
    def vendor(self, outdir: os.PathLike = "", pwd=Global.paths.root):
        cmd = f'{self.binary} mod vendor'
        if outdir:
            out = pathlib.Path(outdir).expanduser().resolve().absolute()
            cmd += f' -o={out}'
        return Shell(cmd=cmd, pwd=pwd)
