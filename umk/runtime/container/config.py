import inspect

from umk import framework, core
from umk.core.errors import ValidationError
from umk.core.typings import Callable, Any
from umk.framework.filesystem import Path
from umk.runtime.container import utils


class ConfigAlreadyRegisteredError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Config is already registered"]


class ConfigIsNotClassError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Use config register for classes based on 'config.Config' only"]


class ConfigBadTypeError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Config class must be based on umk.framework.config.Config"]


class ConfigInvalidSourceError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register config outside of .unimake/config.py"]


class ConfigPresetNotFunctionError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Use config preset register for function with signature 'def (conf: User-Config-Type) -> None' only"]


class ConfigPresetSignatureError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Config preset "]


class ConfigPresetIsOrphanError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Could not register config preset: config type was not registered"]


class ConfigPresetAlreadyExistsError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register config preset: name '{name}' is already exists"]
        self.details.new(name="name", value=name, desc="Config preset name")


class ConfigPresetSourceError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register config preset outside of .unimake/config.py. See preset '{name}'"]
        self.details.new(name="name", value=name, desc="Config preset name")


class Config:
    class Defers:
        def __init__(self):
            self.registerer: utils.Defer | None = None
            self.presets: list[utils.Defer] = []

    def __init__(self):
        self.entries: dict[str, str] = {}
        self.presets: dict[str, Callable[[core.Model], Any]] = {}
        self.struct = None
        self.defers = Config.Defers()
        self.loaded = False

    def set(self, entry: str, value: framework.config.Value):
        if entry not in self.entries:
            core.globals.console.print(f"[yellow bold]Config: '{entry}' entry not found")
            return
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

    def save(self, path: Path = core.globals.paths.config):
        if self.struct:
            core.json.save(self.struct, path, 2)
        else:
            core.globals.console.print("[bold]Config: failed to save config. It is not registered !")

    def load(self, path: Path = core.globals.paths.config):
        if not self.struct:
            core.globals.console.print("[bold yellow]Config: failed to load config. It is not registered !")
            return
        if not path.exists():
            core.globals.console.print("[bold yellow]Config: failed to load config. File does not exists !")
            return

        data = core.json.load(path)
        try:
            value = type(self.struct).model_validate(data)
            self.struct = value
        except ValidationError:
            core.globals.console.print("[red bold]Config: failed to load config. Json file does not compatible to python model")

    def update(self, from_file: bool, presets: list[str], overrides: dict[str, framework.config.Value]):
        if not self.struct:
            return
        if from_file:
            self.load()
        for preset in presets:
            updater = self.presets.get(preset)
            if not updater:
                core.globals.console.print(f"[bold yellow]Config: invalid preset '{preset}'")
            updater(self.struct)
        for k, v in overrides.items():
            self.set(k, v)

    def register(self, factory):
        if self.loaded:
            return factory

        # Allow register just from .unimake/config.py
        frame = inspect.stack()[2]
        if not frame.filename.endswith(".unimake/config.py"):
            raise ConfigInvalidSourceError()

        # Register struct just one time
        if self.defers.registerer:
            raise ConfigAlreadyRegisteredError()

        # Only class is valid subject
        if not inspect.isclass(factory):
            raise ConfigIsNotClassError()

        self.defers.registerer = utils.Defer(func=factory)

        return factory

    def preset(self, func=None, *, name: str = ""):
        def validate(f, n, s):
            # Allow register just from .unimake/config.py
            frame = inspect.stack()[s]
            if not frame.filename.endswith(".unimake/config.py"):
                raise ConfigPresetSourceError(n)

            # Allow only functions
            if not inspect.isfunction(f):
                raise ConfigPresetNotFunctionError()

            # Allow only signature with 1 argument
            sig = len(inspect.signature(f).parameters)
            if sig != 1:
                raise ConfigPresetSignatureError()

        # Without 'name'
        if func is not None:
            if not self.loaded:
                validate(func, func.__name__, 3)
                self.defers.presets.append(utils.Defer(func, name=func.__name__))
            return func

        def decorator(fu):
            # With 'name'
            if not self.loaded:
                # TODO Validate name
                validate(fu, name, 2)
                self.defers.presets.append(utils.Defer(fu, name=name))
            return fu

        return decorator

    def implement(self):
        @core.overload
        def rp(func): ...

        @core.overload
        def rp(*, name: str = ""): ...

        def rp(func=None, *, name: str = ""): return self.preset(func, name=name)

        framework.config.register = lambda factory: self.register(factory)
        framework.config.preset = rp
        framework.config.get = lambda: self.struct

    def run_defers(self):
        if self.defers.registerer:
            self.struct = self.defers.registerer.func()
            if not issubclass(type(self.struct), framework.config.Config):
                raise ConfigBadTypeError()
            self.setup()
        if self.defers.presets:
            if not self.struct:
                raise ConfigPresetIsOrphanError()
            for preset in self.defers.presets:
                name = preset.args.get("name")
                if name in self.presets:
                    raise ConfigPresetAlreadyExistsError(name)
                self.presets[name] = preset.func
