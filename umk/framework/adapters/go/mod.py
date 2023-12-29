import os

from umk import globals, core
from umk.framework.filesystem import Path
from umk.framework.system.shell import Shell


class Mod:
    @core.typeguard
    def __init__(self, binary: Path):
        self.binary = binary

    @core.typeguard
    def tidy(self, compat: str = "", pwd=globals.paths.work) -> Shell:
        cmd = f'{self.binary} mod tidy'
        cpt = compat.strip()
        if cpt:
            cmd += f' -compat={cpt}'
        return Shell(cmd=cmd, cwd=pwd)

    @core.typeguard
    def vendor(self, outdir: os.PathLike = "", pwd=globals.paths.work):
        cmd = f'{self.binary} mod vendor'
        if outdir:
            out = Path(outdir).expanduser().resolve().absolute()
            cmd += f' -o={out}'
        return Shell(
            command=cmd,
            workdir=pwd
        )
