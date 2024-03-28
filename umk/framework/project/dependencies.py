import copy

from umk import core
from umk.core.typings import Callable, Any
from umk.framework.adapters.go import Go
from umk.framework.filesystem import Path
from umk.framework.system import Shell, which, platform


class OsPackageManagerNotFoundError(core.Error):
    def __init__(self, managers: list[str]):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [
            f"Could not found one of package manager: [{', '.join(managers)}]"
        ]


class Dependency(core.Model):
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


class Packages(Dependency):

    class Lists(core.Model):
        apt: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'apt'"
        )
        apt_get: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'apt-get'"
        )
        apk: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'apk'"
        )
        yum: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'yum'"
        )
        dnf: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'dnf'"
        )
        pacman: list[str] = core.Field(
            default_factory=list,
            description="List ot the packages installed by 'pacman'"
        )

    class Managers(core.Model):
        class Manager(core.Model):
            update: Shell = core.Field(
                default_factory=Shell,
                description="Command to update package manager before installation"
            )
            install: Shell = core.Field(
                default_factory=Shell,
                description="Command to install packages"
            )
            clean: Shell = core.Field(
                default_factory=Shell,
                description="Command to clean package manager stuff after installation"
            )

        apt: Manager = core.Field(
            description="'apt' package manager",
            default_factory=lambda: Packages.Manager(
                update=Shell(name="apt", cmd=["apt", "update"]),
                install=Shell(name="apt", cmd=["apt", "-y", "install"]),
                clean=Shell(name="apt:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
            )
        )
        apt_get: Manager = core.Field(
            description="'apt-get' package manager",
            default_factory=lambda: Packages.Manager(
                update=Shell(name="apt-get", cmd=["apt-get", "update"]),
                install=Shell(name="apt-get", cmd=["apt-get", "-y", "install"]),
                clean=Shell(name="apt-get:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
            )
        )
        apk: Manager = core.Field(
            description="'apk' package manager",
            default_factory=lambda: Packages.Manager(
                update=Shell(name="apk", cmd=["apk", "update"]),
                install=Shell(name="apk", cmd=["apk", "add"]),
            )
        )
        yum: Manager = core.Field(
            description="'yum' package manager",
            default_factory=lambda: Packages.Manager(
                update=Shell(name="yum", cmd=["yum", "update"]),
                install=Shell(name="yum", cmd=["yum", "-y", "install"]),
            )
        )
        dnf: Manager = core.Field(
            description="'dnf' package manager",
            default_factory=lambda: Packages.Manager(
                update=Shell(name="dnf", cmd=["dnf", "update"]),
                install=Shell(name="dnf", cmd=["dnf", "-y", "install"]),
            )
        )
        pacman: Manager = core.Field(
            description="'pacman' package manager",
            default_factory=lambda: Packages.Manager(
                install=Shell(name="pacman", cmd=["pacman", "-S", "--noconfirm", "--disable-download-timeout"]),
            )
        )

    packages: Lists = core.Field(
        default_factory=Lists,
        description="Per manager package list"
    )
    managers: Managers = core.Field(
        default_factory=Managers,
        description="Package managers settings"
    )
    sudo: bool = core.Field(
        default=False,
        description="Run commands by super user",
    )

    def resolve(self, **kwargs):
        manager: None | Packages.Managers.Manager = None
        packages = []

        # find existing manager and select its packages
        for name in self.managers.model_fields:
            binary = which(name)
            if binary and binary in self.managers.model_fields:
                manager = copy.deepcopy(getattr(self.managers, name))
                packages = getattr(self.packages, name)
                break

        if not manager:
            raise OsPackageManagerNotFoundError(
                managers=list(self.managers.model_fields.keys())
            )

        # force sudo if required
        if self.sudo and platform().unix:
            manager.update.cmd.insert(0, "sudo")
            manager.clean.cmd.insert(0, "sudo")
            manager.install.cmd.insert(0, "sudo")

        # run package manager 'update'
        if manager.update.cmd:
            manager.update.sync()

        # install packages
        manager.install.cmd += packages
        manager.install.sync()

        # run package manager 'clean'
        if manager.clean.cmd:
            manager.clean.sync()


class GoMod(Dependency):
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
        self.go.shell.workdir = self.path
        self.go.mod.tidy(compat=self.compat)
        if self.vendor:
            self.go.mod.vendor()


class ShellCommand(Dependency):
    shell: Shell = core.Field(
        default_factory=Shell,
        description="Shell to run"
    )

    def resolve(self, **kwargs):
        if self.shell.cmd:
            self.shell.sync()


class Function(Dependency):
    function: Callable[[], Any] = core.Field(
        default=None,
        description="Function to run"
    )

    def resolve(self, **kwargs):
        if self.function:
            self.function()


# class Builder:
#     class Go:
#         def __init__(self):
#             self.mod = GoMod(name="go", description="Golang 'go.mod' file")
#
#     def __init__(self):
#         self.go = Builder.Go()
#         self.os = Packages(name="os", description="Operating system packages")
#
#     def build(self) -> list[Dependency]:
#         result = []
#         if self.go.mod.path:
#             result.append(self.go.mod)
#         os = any((
#             self.os.packages.apt,
#             self.os.packages.apt_get,
#             self.os.packages.apk,
#             self.os.packages.dnf,
#             self.os.packages.yum,
#             self.os.packages.pacman
#         ))
#         if os:
#             result.append(self.os)
#         return result
#
#
# b = Builder()