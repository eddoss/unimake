import os
from textwrap import dedent
from umk import core
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface
from umk.framework.remote.docker.container import Container
from umk.framework.adapters.docker import file as dockerfile


class File(Container):
    file: dockerfile.File = core.Field(
        description="Dockerfile adapter",
        default_factory=dockerfile.File
    )
    path: Path = core.Field(
        description="Dockerfile path",
        default=Path("Dockerfile")
    )

    @core.typeguard
    def __init__(
        self,
        name: str = "",
        description: str = "Docker container environment",
        default: bool = False,
        container: str = "",
        shell: str = "sh",
        path: Path = Path("Dockerfile"),
    ):
        super().__init__(
            name=name,
            default=default,
            description=description,
            command=["docker"],
            sh=shell
        )
        self.container = container
        self.path = path

    def build(self, **kwargs):
        with open(self.path, "w", encoding="utf-8") as stream:
            self.file.write(stream)

    def destroy(self, **kwargs):
        super().destroy(**kwargs)

    def up(self, **kwargs):
        super().up(**kwargs)

    def down(self, **kwargs):
        super().down(**kwargs)

    def _register_properties(self):
        super()._register_properties()
        self._properties.add("file")
        self._properties.add("path")

