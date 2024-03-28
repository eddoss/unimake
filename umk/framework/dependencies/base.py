import copy

from umk import core
from umk.core.typings import Callable, Any
from umk.framework.adapters.go import Go
from umk.framework.filesystem import Path, AnyPath
from umk.framework.system import Shell, which, platform, Environs


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


class PackageManager(core.Model):
    binary: str = core.Field(
        default="",
        description="Package manager binary"
    )
    before: Shell = core.Field(
        default_factory=Shell,
        description="Command to run before packages installation"
    )
    install: Shell = core.Field(
        default_factory=Shell,
        description="Command to install packages"
    )
    after: Shell = core.Field(
        default_factory=Shell,
        description="Command to run after packages installation"
    )


class AbstractOsPackages(Interface):
    manager: PackageManager = core.Field(
        default=None,
        description="Package manager commands",
    )
    items: list[str] = core.Field(
        default_factory=list,
        description="List ot the packages to install"
    )
    sudo: bool = core.Field(
        default=False,
        description="Run shell by super user"
    )

    def resolve(self, **kwargs):
        if not self.manager.binary.strip():
            err = core.Error(name="PackageManagerBinaryIsEmpty")
            err.messages.append("Package manager binary is empty. Specify it (apt, apt-get, yum, ...)")
            raise err

        binary = which(self.manager.binary)
        if binary is None:
            core.globals.console.print(
                f"[bold cyan]Skip '{self.manager.binary}' packages, binary nof found"
            )
            return

        if not self.list:
            core.globals.console.print(
                f"[bold cyan]Skip '{self.manager.binary}' packages, no packages were given"
            )
            return

        # set sudo if required
        manager = copy.deepcopy(self.manager)
        if manager.before.cmd and self.sudo and platform().unix:
            manager.update.cmd.insert(0, "sudo")
        if manager.after.cmd and self.sudo and platform().unix:
            manager.after.cmd.insert(0, "sudo")
        if manager.install.cmd and self.sudo and platform().unix:
            manager.install.cmd.insert(0, "sudo")

        # run 'before' command
        if manager.before.cmd:
            manager.before.sync()

        # install packages
        manager.install.cmd += self.list
        manager.install.sync()

        # run 'after' command
        if manager.clean.cmd:
            manager.clean.sync()


class AptPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Apt package manager",
        default_factory=lambda: PackageManager(
            binary="apt",
            before=Shell(name="apt", cmd=["apt", "-y", "update"]),
            after=Shell(name="apt", cmd=["apt", "-y", "install"]),
            install=Shell(name="apt:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
        )
    )


class AptGetPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Apt-get package manager",
        default_factory=lambda: PackageManager(
            binary="apt-get",
            before=Shell(name="apt-get", cmd=["apt-get", "-y", "update"]),
            after=Shell(name="apt-get", cmd=["apt-get", "-y", "install"]),
            install=Shell(name="apt-get:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
        )
    )


class ApkPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Apk package manager",
        default_factory=lambda: PackageManager(
            binary="apk",
            before=Shell(name="apk", cmd=["apk", "update"]),
            after=Shell(name="apk", cmd=["apk", "add"]),
        )
    )


class YumPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Yum package manager",
        default_factory=lambda: PackageManager(
            binary="yum",
            before=Shell(name="yum", cmd=["yum", "-y", "update"]),
            after=Shell(name="yum", cmd=["yum", "-y", "install"]),
        )
    )


class DnfPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Dnf package manager",
        default_factory=lambda: PackageManager(
            binary="dnf",
            before=Shell(name="dnf", cmd=["dnf", "-y", "update"]),
            after=Shell(name="dnf", cmd=["dnf", "-y", "install"]),
        )
    )


class PacmanPackages(AbstractOsPackages):
    manager: PackageManager = core.Field(
        description="Pacman package manager",
        default_factory=lambda: PackageManager(
            binary="pacman",
            after=Shell(name="pacman", cmd=["pacman", "-S", "--noconfirm", "--disable-download-timeout"]),
        )
    )


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
def apt(*packages, sudo=False, name="apt", description="Operating system 'apt' packages") -> AptPackages:
    return AptPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def apt_get(*packages, sudo=False, name="apt-get", description="Operating system 'apt-get' packages") -> AptGetPackages:
    return AptGetPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def apk(*packages, sudo=False, name="apk", description="Operating system 'apk' packages") -> ApkPackages:
    return ApkPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def yum(*packages, sudo=False, name="yum", description="Operating system 'yum' packages") -> YumPackages:
    return YumPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def dnf(*packages, sudo=False, name="dnf", description="Operating system 'dnf' packages") -> DnfPackages:
    return DnfPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def pacman(*packages, sudo=False, name="pacman", description="Operating system 'pacman' packages") -> PacmanPackages:
    return PacmanPackages(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


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
