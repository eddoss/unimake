import inspect

from umk import framework, core
from umk.core.typings import Generator


class Targets:
    def __init__(self):
        self.items: dict[str, framework.targets.Interface] = {}
        self.config = None
        self.project = None

    def objects(self) -> Generator[framework.targets.Interface, None, None]:
        for item in self.items.values():
            yield item.object()

    def __iter__(self) -> framework.targets.Interface:
        for impl in self.items:
            yield impl

    def __contains__(self, name: str):
        return name in self.items

    def __getitem__(self, name: str) -> framework.targets.Interface:
        return self.items[name]

    def get(self, name: str, on_err=None) -> framework.targets.Interface:
        return self.items.get(name, on_err)

    def run(self, name: str):
        target = self.get(name)
        if target is None:
            core.globals.console.print(
                f"[yellow bold]Targets: could not run '{name}', target not found"
            )
            return
        target.run()

    def add(self, impl: framework.targets.Interface):
        if impl.name in self.items:
            # TODO Raise error instead this error
            core.globals.console.print(f"[red bold]Targets: target '{impl.name}' is already exists")
            core.globals.close(-1)
        else:
            self.items[impl.name] = impl

    def function(self, func=None, *, name: str = "", label: str = "", description: str = ""):
        # Without 'name'
        if func is not None:
            impl = framework.targets.Function(name=func.__name__, label=label, description=description, function=func)
            self.add(impl)
            return func

        def decorator(fu):
            # With 'name'
            impl = framework.targets.Function(name=name, label=label, description=description, function=fu)
            self.add(impl)
            return fu

        return decorator

    def register(self, factory):
        sig = len(inspect.signature(factory).parameters)
        if sig == 0:
            impls: framework.targets.Interface = factory()
        elif sig == 1:
            impls: framework.targets.Interface = factory(self.project)
        else:
            impls: framework.targets.Interface = factory(self.project, self.config)

        # TODO Validate func result type and value
        t = type(impls)
        if not issubclass(t, (tuple, list, set)):
            impls = [impls]
        for impl in impls:
            if not impl.label:
                impl.label = impl.name.replace(".", " ").replace("-", " ").replace("_", " ")
            if not impl.description:
                impl.description = factory.__doc__ or ""
            self.add(impl)

    def implement(self):
        @core.overload
        def fnc(func): ...

        @core.overload
        def fnc(*, name: str = "", label: str = "", description: str = ""): ...

        def fnc(func=None, *, name: str = "", label: str = "", description: str = ""): return self.function(func, name=name, label=label, description=description)

        framework.targets.function = fnc
        framework.targets.register = lambda factory: self.register(factory)
