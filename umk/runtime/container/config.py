import inspect

from umk import framework, core
from umk.core.errors import ValidationError
from umk.core.typings import Callable, Any
from umk.framework.filesystem import Path


class Config:
    def __init__(self):
        self.entries: dict[str, str] = {}
        self.presets: dict[str, Callable[core.Model], ...] = {}
        self.struct = None

    def set(self, entry: str, value: framework.config.Value):
        if entry not in self.entries:
            # TODO Raise entry access error
            pass
        tokens = entry.replace("-", "_").split(".")
        if len(tokens) == 1:
            setattr(self.struct, tokens[0], value)
        else:
            attr = tokens[-1]
            curr = self.struct
            for token in tokens[:-1]:
                curr = getattr(curr, token)
            setattr(curr, attr, value)

    def get(self, entry: str, on_err: Any = None) -> None | framework.config.Value:
        if entry not in self.entries:
            return on_err
        result = self.struct
        tokens = entry.replace("-", "_").split(".")
        for token in tokens:
            result = getattr(result, token)
        return result

    def override(self, *overrides: dict[str, framework.config.Value]):
        for override in overrides:
            for k, v in override.items():
                self.set(k, v)

    def setup(self):
        self.entries = {}

        def recursive(root: core.Model, parent: str, tokens: dict[str, str]):
            for n, f in root.model_fields.items():
                v = getattr(root, n)
                t = type(v)
                if t in (str, int, bool, float):
                    token = f"{parent}.{n}".lstrip(".").replace("_", "-")
                    tokens[token] = f.description or ""
                elif issubclass(t, core.Model):
                    recursive(v, f"{parent}.{n}", tokens)
        recursive(self.struct, "", self.entries)

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "UserConfig"
        for name, description in self.entries.items():
            prop = core.Property()
            prop.name = name
            prop.description = description
            prop.value = self.get(name)
            result.properties.add(prop)
        return result

    def register(self, factory):
        # TODO Raise error if 'self.instance.struct' is already exists
        # TODO Validate factory type (expect class but not a function)
        # TODO Validate factory result type (must be a subclass of 'config.Config')

        # we should register struct just one time
        if self.struct is None:
            self.struct = factory()
            self.setup()

        return factory

    def preset(self, func=None, *, name: str = ""):
        sig = inspect.signature(func).parameters
        if len(sig) != 1:
            # TODO Raise error instead this message
            core.globals.console.print(
                "[bold red]Config: failed to register preset.\n"
                f"Invalid function ({func.__name__}) signature, it must accept just config.\n\n"
            )
            core.globals.close(-1)

        # Without 'name'
        if func is not None:
            self.presets[func.__name__.replace("_", "-")] = func
            return func

        def decorator(fu):
            # With 'name'
            # TODO Validate name
            self.presets[name] = fu
            return fu

        return decorator

    def save(self, path: Path = core.globals.paths.config):
        if self.struct:
            core.json.save(self.struct, path, 2)
        else:
            core.globals.console.print("[bold]Config: failed to save config. It is not registered !")

    def load(self, path: Path = core.globals.paths.config):
        if not self.struct:
            core.globals.console.print("[bold]Config: failed to load config. It is not registered !")
            return
        if not path.exists():
            core.globals.console.print("[bold]Config: failed to load config. File does not exists !")
            return

        data = core.json.load(path)
        try:
            self.struct = type(self.struct).model_validate(data)
        except ValidationError:
            core.globals.console.print("[red bold]Config: failed to load config. Json file does not compatible to python model")

    def implement(self):
        @core.overload
        def rp(func): ...

        @core.overload
        def rp(*, name: str = ""): ...

        def rp(func=None, *, name: str = ""): return self.preset(func, name=name)

        framework.config.register = lambda factory: self.register(factory)
        framework.config.preset = rp
        framework.config.get = lambda: self.struct
