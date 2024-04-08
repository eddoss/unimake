from umk import core
from umk.core.typings import Callable, Any, Generator
from umk.framework.adapters.go import Go
from umk.framework.filesystem import Path, AnyPath
from umk.framework.dependencies.base import Interface, GoMod, Function, Command
from umk.framework.dependencies.packages import Apt, AptGet, Apk, Yum, Dnf, Pacman
from umk.framework.system import Environs, Shell


class Group(core.Model):
    name: str = core.Field(
        default="",
        description="Group name"
    )
    items: list[Interface] = core.Field(
        default_factory=list,
        description="Dependency list"
    )
    
    def __len__(self):
        return len(self.items)
    
    def __iter__(self):
        for item in self.items:
            yield item
    
    def resolve(self, **kwargs):
        for item in self.items:
            item.resolve(**kwargs)

    @core.typeguard
    def apt(self, *packages, sudo=False, name="apt", description="Operating system 'apt' packages"):
        self.items.append(
            Apt(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def apt_get(self, *packages, sudo=False, name="apt-get", description="Operating system 'apt-get' packages"):
        self.items.append(
            AptGet(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def apk(self, *packages, sudo=False, name="apk", description="Operating system 'apk' packages"):
        self.items.append(
            Apk(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def yum(self, *packages, sudo=False, name="yum", description="Operating system 'yum' packages"):
        self.items.append(
            Yum(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def dnf(self, *packages, sudo=False, name="dnf", description="Operating system 'dnf' packages"):
        self.items.append(
            Dnf(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def pacman(self, *packages, sudo=False, name="pacman", description="Operating system 'pacman' packages"):
        self.items.append(
            Pacman(
                name=name,
                description=description,
                sudo=sudo,
                items=list(packages)
            )
        )

    @core.typeguard
    def gomod(self, path: AnyPath, tool: Go, vendor=False, compat="", name="go.mod", description="Golang packages from 'go.mod'"):
        self.items.append(
            GoMod(
                name=name,
                description=description,
                tool=tool,
                path=path,
                compat=compat,
                vendor=vendor
            )
        )

    @core.typeguard
    def command(
            self,
            cmd: list[str | Path],
            workdir: None | Path = None,
            environs: None | Environs = None,
            shell_name: str = "dep:command",
            name="command",
            description="Shell command"
    ):
        self.items.append(
            Command(
                name=name,
                description=description,
                shell=Shell(
                    name=shell_name,
                    cmd=cmd,
                    workdir=workdir,
                    environs=environs,
                )
            )
        )

    @core.typeguard
    def function(self, func: Callable[[], Any], name="function", description="Custom pyhon function"):
        self.items.append(
            Function(
                name=name,
                description=description,
                function=func
            )
        )


class Container:
    def __init__(self):
        self._groups: dict[str, Group] = {}
    
    def __len__(self):
        return len(self._groups)

    def __setitem__(self, group: Group):
        self._groups[group.name] = group

    def __getitem__(self, group: str):
        name = group.strip()
        if name not in self._groups:
            self._groups[name] = Group(name=name)
        return self._groups[name]

    def __contains__(self, group: str):
        return group in self._groups

    def groups(self) -> Generator[Group, None, None]:
        for group in self._groups.values():
            yield group

    def items(self) -> Generator[Interface, None, None]:
        for group in self._groups.values():
            for item in group.items:
                yield item

    def resolve(self, **kwargs):
        for group in self._groups.values():
            group.resolve(**kwargs)
