import inspect

from umk import framework, core
from umk.core.typings import Generator
from umk.runtime.container import utils


class TargetAlreadyExistsError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Target '{name}' is already registered"]


class TargetSourceError(core.Error):
    def __init__(self, name: str = ""):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        if name:
            self.messages = [f"Could not register project target outside of .unimake/project.py. See preset '{name}'"]
            self.details.new(name="name", value=name, desc="Target name")
        else:
            self.messages = [f"Could not register project target outside of .unimake/project.py"]


class TargetNotFunctionError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project target, only functions are allowed. See '{name}'"]
        self.details.new(name="name", value=name, desc="Target name")


class Targets:
    class Defers:
        def __init__(self):
            self.objects: list[utils.Defer] = []
            self.functions: list[utils.Defer] = []

    def __init__(self):
        self._items: dict[str, framework.targets.Interface] = {}
        self.loaded = False
        self.defers = Targets.Defers()

    def __iter__(self) -> Generator[framework.targets.Interface, None, None]:
        for item in self._items.values():
            yield item

    def __contains__(self, name: str):
        return name in self._items

    def __getitem__(self, name: str) -> framework.targets.Interface:
        return self._items[name]

    def objects(self) -> Generator[framework.targets.Interface, None, None]:
        for item in self._items.values():
            yield item.object()

    def get(self, name: str, on_err=None) -> framework.targets.Interface:
        return self._items.get(name, on_err)

    def run(self, *names: str):
        found = []
        for name in names:
            if name not in self._items:
                core.globals.console.print(f"[yellow bold]Target '{name}' not found")
            else:
                found.append(name)
        for name in found:
            target = self.get(name)
            target.run(p=framework.project.get(), c=framework.config.get())

    def function(self, func=None, *, name: str = "", label: str = "", description: str = ""):
        def validate(f, n, s):
            # Allow register just from .unimake/project.py
            frame = inspect.stack()[s]
            if not frame.filename.endswith(".unimake/project.py"):
                raise TargetSourceError(n)

            # Allow only functions
            if not inspect.isfunction(f):
                raise TargetNotFunctionError(n)

        # Without args
        if func is not None:
            if not self.loaded:
                n: str = func.__name__
                n = n.replace("_", "-")
                n = n.lower()
                l = n.replace("-", " ").capitalize()
                d = func.__doc__ or ""
                d = d.strip()
                validate(func, n, 3)
                self.defers.functions.append(utils.Defer(
                    func=func, name=n, label=l, description=d
                ))
            return func

        def decorator(fu):
            # With args
            if not self.loaded:
                n: str = name or fu.__name__.lower().replace("_", "-")
                l = label or n.replace("-", " ").capitalize()
                d = description or fu.__doc__ or ""
                d = d.strip()
                validate(fu, n, 2)
                self.defers.functions.append(utils.Defer(
                    func=fu, name=n, label=l, description=d
                ))
            return fu

        return decorator

    def register(self, factory):
        if self.loaded:
            return factory

        # Allow register just from .unimake/project.py
        frame = inspect.stack()[2]
        if not frame.filename.endswith(".unimake/project.py"):
            raise TargetSourceError()

        self.defers.objects.append(utils.Defer(func=factory))

        return factory

    def implement(self):
        @core.overload
        def fnc(func): ...

        @core.overload
        def fnc(*, name: str = "", label: str = "", description: str = ""): ...

        def fnc(func=None, *, name: str = "", label: str = "", description: str = ""): return self.function(func, name=name, label=label, description=description)

        framework.targets.function = fnc
        framework.targets.register = lambda factory: self.register(factory)

    def run_defers(self):
        for defer in self.defers.functions:
            target = framework.targets.Function(
                name=defer.args.get("name"),
                description=defer.args.get("description"),
                label=defer.args.get("label"),
                function=defer.func
            )
            if target.name in self._items:
                raise TargetAlreadyExistsError(target.name)
            self._items[target.name] = target

        for defer in self.defers.objects:
            targets: framework.targets.Interface | list[framework.targets.Interface] | None = None
            sig = len(inspect.signature(defer.func).parameters)
            if sig == 0:
                targets = defer.func()
            elif sig == 1:
                targets = defer.func(framework.config.get())
            else:
                targets = defer.func(framework.config.get(), framework.project.get())
            if not issubclass(type(targets), (tuple, list, set)):
                targets = [targets]
            for target in targets:
                if target.name in self._items:
                    raise TargetAlreadyExistsError(target.name)
                if not target.label:
                    target.label = target.name.replace(".", " ").replace("-", " ").replace("_", " ")
            for target in targets:
                if target.name in self._items:
                    raise TargetAlreadyExistsError(target.name)
                self._items[target.name] = target
