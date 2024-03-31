import copy

from umk import core
from umk.framework.dependencies import base
from umk.framework.system import Shell, which, platform


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


class Abstract(base.Interface):
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

        if not self.items:
            core.globals.console.print(
                f"[bold cyan]Skip '{self.manager.binary}' packages, no packages were given"
            )
            return

        # set sudo if required
        manager = copy.deepcopy(self.manager)
        if self.sudo and platform().unix:
            if manager.before.cmd:
                manager.before.cmd.insert(0, "sudo")
            if manager.after.cmd:
                manager.after.cmd.insert(0, "sudo")
            if manager.install.cmd:
                manager.install.cmd.insert(0, "sudo")

        # run 'before' command
        if manager.before.cmd:
            manager.before.sync()

        # install packages
        manager.install.cmd += self.items
        manager.install.sync()

        # run 'after' command
        if manager.after.cmd:
            manager.after.sync()


class Apt(Abstract):
    manager: PackageManager = core.Field(
        description="Apt package manager",
        default_factory=lambda: PackageManager(
            binary="apt",
            before=Shell(name="apt", cmd=["apt", "-y", "update"]),
            after=Shell(name="apt", cmd=["apt", "-y", "install"]),
            install=Shell(name="apt:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
        )
    )


class AptGet(Abstract):
    manager: PackageManager = core.Field(
        description="Apt-get package manager",
        default_factory=lambda: PackageManager(
            binary="apt-get",
            before=Shell(name="apt-get", cmd=["apt-get", "-y", "update"]),
            after=Shell(name="apt-get", cmd=["apt-get", "-y", "install"]),
            install=Shell(name="apt-get:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
        )
    )


class Apk(Abstract):
    manager: PackageManager = core.Field(
        description="Apk package manager",
        default_factory=lambda: PackageManager(
            binary="apk",
            before=Shell(name="apk", cmd=["apk", "update"]),
            after=Shell(name="apk", cmd=["apk", "add"]),
        )
    )


class Yum(Abstract):
    manager: PackageManager = core.Field(
        description="Yum package manager",
        default_factory=lambda: PackageManager(
            binary="yum",
            before=Shell(name="yum", cmd=["yum", "-y", "update"]),
            after=Shell(name="yum", cmd=["yum", "-y", "install"]),
        )
    )


class Dnf(Abstract):
    manager: PackageManager = core.Field(
        description="Dnf package manager",
        default_factory=lambda: PackageManager(
            binary="dnf",
            before=Shell(name="dnf", cmd=["dnf", "-y", "update"]),
            after=Shell(name="dnf", cmd=["dnf", "-y", "install"]),
        )
    )


class Pacman(Abstract):
    manager: PackageManager = core.Field(
        description="Pacman package manager",
        default_factory=lambda: PackageManager(
            binary="pacman",
            after=Shell(name="pacman", cmd=["pacman", "-S", "--noconfirm", "--disable-download-timeout"]),
        )
    )


@core.typeguard
def apt(*packages, sudo=False, name="apt", description="Operating system 'apt' packages") -> Apt:
    return Apt(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def apt_get(*packages, sudo=False, name="apt-get", description="Operating system 'apt-get' packages") -> AptGet:
    return AptGet(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def apk(*packages, sudo=False, name="apk", description="Operating system 'apk' packages") -> Apk:
    return Apk(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def yum(*packages, sudo=False, name="yum", description="Operating system 'yum' packages") -> Yum:
    return Yum(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def dnf(*packages, sudo=False, name="dnf", description="Operating system 'dnf' packages") -> Dnf:
    return Dnf(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )


@core.typeguard
def pacman(*packages, sudo=False, name="pacman", description="Operating system 'pacman' packages") -> Pacman:
    return Pacman(
        name=name,
        description=description,
        sudo=sudo,
        items=list(packages)
    )
