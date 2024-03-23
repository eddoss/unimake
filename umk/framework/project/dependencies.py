from umk import core
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

    def install(self, **kwargs):
        raise NotImplemented()


class Packages(Dependency):
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
    sudo: bool = core.Field(
        default=False,
        description="Run installation by super user"
    )

    def install(self, **kwargs):
        manager, shell = self.manager()
        if self.sudo and platform().unix:
            shell.cmd.insert(0, "sudo")
        packages = getattr(self, manager)
        shell.cmd += packages
        shell.sync()

    def manager(self) -> tuple[str, Shell]:
        shells = {
            "apt": Shell(cmd=["install", "-y"]),
            "apt-get": Shell(cmd=["install", "-y"]),
            "apk": Shell(cmd=["add"]),
            "yum": Shell(cmd=["-y", "install"]),
            "dnf": Shell(cmd=["install"]),
            "pacman": Shell(cmd=["-S", "--noconfirm", "--disable-download-timeout"]),
        }
        for manager, shell in shells.items():
            binary = which(manager)
            if binary:
                shell.cmd.insert(0, manager)
                return manager, shell
        raise OsPackageManagerNotFoundError(list(shells.keys()))
