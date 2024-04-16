import copy

from umk import core
from umk.framework.target.interface import Interface
from umk.framework.system.shell import Shell
from umk.framework.system.platform import platform
from shutil import which


class Manager(core.Model):
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

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "SystemPackageManager"
        result.properties.new("Binary", self.binary, "Package manager binary")
        result.properties.new("Before", self.before.cmd, "Package manager 'before' command")
        result.properties.new("After", self.after.cmd, "Package manager 'after' command")
        result.properties.new("Install", self.install.cmd, "Package manager 'install' command")
        return result


class PackageList(core.Model):
    manager: Manager = core.Field(
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

    def install(self, **kwargs):
        if not self.items:
            core.globals.console.print(
                f"[bold cyan]Skip '{self.manager.binary}' packages, list is empty"
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

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "SystemPackageList"
        result.properties.new("Sudo", self.sudo, "Run manager commands by super user")
        result.properties.new("Manager", self.manager.object(), "Package manager info")
        result.properties.new("Items", self.items, "Package list")
        return result


class SystemPackages(Interface):
    apt: PackageList = core.Field(
        description="Apt package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="apt",
                before=Shell(name="apt", cmd=["apt", "-y", "update"]),
                install=Shell(name="apt", cmd=["apt", "-y", "install"]),
                after=Shell(name="apt:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
            )
        )
    )
    apt_get: PackageList = core.Field(
        description="Apt-get package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="apt-get",
                before=Shell(name="apt-get", cmd=["apt-get", "-y", "update"]),
                install=Shell(name="apt-get", cmd=["apt-get", "-y", "install"]),
                after=Shell(name="apt-get:clean", cmd=["rm", "-r", "-f", "/var/lib/apt/lists/*"]),
            )
        )
    )
    apk: PackageList = core.Field(
        description="Apk package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="apk",
                before=Shell(name="apk", cmd=["apk", "update"]),
                install=Shell(name="apk", cmd=["apk", "add"]),
            )
        )
    )
    yum: PackageList = core.Field(
        description="Yum package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="yum",
                before=Shell(name="yum", cmd=["yum", "-y", "update"]),
                install=Shell(name="yum", cmd=["yum", "-y", "install"]),
            )
        )
    )
    dnf: PackageList = core.Field(
        description="Dnf package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="dnf",
                before=Shell(name="dnf", cmd=["dnf", "-y", "update"]),
                install=Shell(name="dnf", cmd=["dnf", "-y", "install"]),
            )
        )
    )
    pacman: PackageList = core.Field(
        description="Pacman package manager",
        default_factory=lambda: PackageList(
            manager=Manager(
                binary="pacman",
                install=Shell(name="pacman", cmd=["pacman", "-S", "--noconfirm", "--disable-download-timeout"]),
            )
        )
    )

    def run(self, **kwargs):
        managers = ("apt-get", "apt", "apk", "yum", "dnf", "pacman")
        binary = None
        for entry in managers:
            binary = which(entry)
            if binary:
                binary = entry
                break
        if binary is None:
            core.globals.console.print(f"[yellow bold]Failed to install packages: no package manager was found !")
            core.globals.console.print(f"[yellow bold]Found one of: {', '.join(managers)}")
            return
        core.globals.console.print(f"[cyan bold]Found '{binary}' package manager")
        pl: PackageList = getattr(self, binary.replace("-", "_"))
        pl.install()

    def object(self, **kwargs) -> core.Object:
        result = core.Object()
        result.type = "Target.SystemPackages"
        result.properties.new("apt", self.apt.items, "apt packages")
        result.properties.new("apt-get", self.apt_get.items, "apt-get packages")
        result.properties.new("apk", self.apk.items, "apk packages")
        result.properties.new("dnf", self.dnf.items, "dnf packages")
        result.properties.new("yum", self.yum.items, "yum packages")
        result.properties.new("pacman", self.pacman.items, "pacman packages")
        return result



