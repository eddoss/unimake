import abc

from umk import core
from umk.core.typings import Generator, Any, Callable
from umk.framework.adapters import go
from umk.framework.filesystem import Path
from umk.framework.system import Environs
from umk.framework.system import Shell
from umk.framework.targets.golang import GolangBinary
from umk.framework.targets.interface import Interface
from umk.framework.targets.interface import Command
from umk.framework.targets.interface import Function


def already_exists_warning(name: str):
    core.globals.console.print(
        f"[yellow bold]Targets: target '{name}' is already exists"
    )


class Container:
    class GoTargets:
        def __init__(self, items: dict[str, Interface]):
            self._items = items

        @core.typeguard
        def binary(self, *, name: str, tool: go.Go, build: go.Build, debug: bool = True, port: int = 2345, label: str = "", description: str = ""):
            base = GolangBinary(
                name=name.strip(),
                label=label.strip(),
                description=description.strip(),
                tool=tool,
                build=build,
                debug=GolangBinary.Debug(port=port)
            )
            if not base.label:
                base.label = f"Binary '{base.name}'"
            if not base.description:
                base.description = f"Golang binary ({base.name})"

            if debug:
                if name in self._items:
                    already_exists_warning(name)
                else:
                    debug = base.model_copy()
                    debug.name = name
                    debug.build.flags.gc.append('all=-N')
                    debug.build.flags.gc.append('-l')
                    self._items[debug.name] = debug

                name = name + ".release"
                if name in self._items:
                    already_exists_warning(name)
                else:
                    release = base.model_copy()
                    release.name = name
                    release.build.flags.gc.append('-dwarf=false')
                    release.build.flags.ld.append('-s')
                    release.build.flags.ld.append('-w')
                    self._items[release.name] = release
            else:
                if base.name in self._items:
                    already_exists_warning(base.name)
                else:
                    self._items[base.name] = base

    def __init__(self):
        self._items: dict[str, Interface] = {}
        self.go = Container.GoTargets(self._items)

    def objects(self) -> Generator[Interface, None, None]:
        for item in self._items.values():
            yield item.object()

    def __iter__(self) -> Interface:
        for impl in self._items:
            yield impl

    def __contains__(self, name: str):
        return name in self._items

    def __getitem__(self, name: str) -> Interface:
        return self._items[name]

    def get(self, name: str, on_err=None) -> Interface:
        return self._items.get(name, on_err)

    def run(self, name: str):
        target = self.get(name)
        if target is None:
            core.globals.console.print(
                f"[yellow bold]Targets: could not run '{name}', target not found"
            )
            return
        target.run()

    def command(
        self,
        *,
        name: str,
        cmd: list[str | Path],
        workdir: None | Path = None,
        environs: None | Environs = None,
        label: str = "",
        description: str = ""
    ):
        if name in self._items:
            already_exists_warning(name)
            return

        target = Command(
            name=name.strip(),
            label=label.strip(),
            description=description.strip(),
            shell=Shell(
                cmd=cmd,
                workdir=workdir,
                environs=environs,
            )
        )
        self._items[target.name] = target

    def function(
        self,
        *,
        name: str,
        function: Callable[[...], Any],
        label: str = "",
        description: str = ""
    ):
        if name in self._items:
            already_exists_warning(name)
            return
        target = Function(
            name=name.strip(),
            label=label.strip(),
            description=description.strip(),
            function=function,
        )
        self._items[target.name] = target
