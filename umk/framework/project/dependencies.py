import copy

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

    def install(self, **kwargs):
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
