from umk import core
from umk.core.typings import Callable, Any
from umk.framework.adapters.go import Go
from umk.framework.filesystem import Path, AnyPath
from umk.framework.system import Shell, Environs


class Interface(core.Model):
    name: str = core.Field(
        default="",
        description="Dependency name"
    )
    description: str = core.Field(
        default="",
        description="Dependency description"
    )

    def resolve(self, **kwargs):
        raise NotImplemented()


class GoMod(Interface):
    tool: Go = core.Field(
        default_factory=Go,
        description="Go tool object"
    )
    path: None | Path = core.Field(
        default=None,
        description="Path to directory with go.mod"
    )
    compat: str = core.Field(
        default="",
        description="Preserves any additional checksums (see 'go help mod tidy')"
    )
    vendor: bool = core.Field(
        default=False,
        description="Vendor downloaded packages"
    )

    def resolve(self, **kwargs):
        self.tool.shell.workdir = self.path
        self.tool.mod.tidy(compat=self.compat)
        if self.vendor:
            self.tool.mod.vendor()


class Command(Interface):
    shell: Shell = core.Field(
        default_factory=Shell,
        description="Shell to run"
    )

    def resolve(self, **kwargs):
        if self.shell.cmd:
            self.shell.sync()


class Function(Interface):
    function: Callable[[], Any] = core.Field(
        default=None,
        description="Function to run"
    )

    def resolve(self, **kwargs):
        if self.function:
            self.function()


@core.typeguard
def gomod(path: AnyPath, tool: Go, vendor=False, compat="", name="go.mod", description="Golang packages from 'go.mod'") -> GoMod:
    return GoMod(
        name=name,
        description=description,
        tool=tool,
        path=path,
        compat=compat,
        vendor=vendor
    )


@core.typeguard
def command(
    cmd: list[str | Path],
    workdir: None | Path = None,
    environs: None | Environs = None,
    shell_name: str = "dep:command",
    name="command",
    description="Shell command"
) -> Command:
    return Command(
        name=name,
        description=description,
        shell=Shell(
            name=shell_name,
            cmd=cmd,
            workdir=workdir,
            environs=environs,
        )
    )


@core.typeguard
def function(func: Callable[[], Any], name="function", description="Custom pyhon function") -> Function:
    return Function(
        name=name,
        description=description,
        function=func
    )
