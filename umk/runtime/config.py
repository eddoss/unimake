import os
import sys

from pydantic import ValidationError

from umk import core
from umk.kit import config
from umk.core.typings import Callable, Any, Type
from umk.framework.filesystem import Path
from umk.runtime import utils


class Config(core.Model):
    class Update(core.Model):
        overrides: dict[str, config.Value] = core.Field(
            default_factory=dict,
            description="Config entry overrides (passed by unimake CLI)"
        )
        presets: list[str] = core.Field(
            default_factory=list,
            description="Config presets to apply (passed by unimake CLI)"
        )
        file: bool = core.Field(
            default=False,
            description="Load config from file and modify it by preset and overrides"
        )

    class Decorators(core.Model):
        instance: utils.Decorator = core.Field(
            description="Decorator of the config structure",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="class",
                    base=config.Interface,
                ),
                module="config",
                single=True,
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register config outside of the .unimake/config.py"),
                    subject=utils.ClassError("Failed to register config. Use 'framework.config.register' with functions")
                )
            ),
        )
        preset: utils.Decorator = core.Field(
            description="Decorator of the config preset",
            default_factory=lambda: utils.Decorator(
                stack=2,
                module="config",
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register config preset outside of the .unimake/project.py"),
                    sig=utils.SignatureError("Failed to register config preset. Function must accept 1 argument at least"),
                )
            )
        )

    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Project decorators"
    )
    instance: config.Interface | None = core.Field(
        default=None,
        description="Config instance"
    )
    presets: dict[str, Callable[[config.Interface], Any]] = core.Field(
        default_factory=dict,
        description="Config presets"
    )
    entries: dict[str, str] = core.Field(
        default_factory=dict,
        description="Config entries"
    )

    def set(self, entry: str, value: str):
        if entry not in self.entries:
            core.globals.console.print(f"[yellow bold]Config: '{entry}' entry not found")
            return

        def find() -> tuple[Any, str, Type]:
            tokens = entry.replace("-", "_").split(".")
            attr = tokens[-1]
            curr = self.instance
            for token in tokens[:-1]:
                curr = getattr(curr, token)
            return curr, attr, type(getattr(curr, attr))

        def assign(to: Any, which: str, what: str, t: Type):
            if t == str:
                setattr(to, which, what)
            elif t == int:
                setattr(to, which, int(what))
            elif t == bool:
                if what == "yes":
                    setattr(to, which, True)
                elif what == "no":
                    setattr(to, which, False)
                else:
                    raise core.Error(
                        "BadBool",
                        f"Failed to set config entry '{entry}' value",
                        "Valid boolean: 'yes', 'no'",
                        f"Given: {value}"
                    )
            elif t == float:
                setattr(to, which, float(what))

        obj, name, typ = find()
        assign(obj, name, value, typ)

    def get(self, entry: str, on_err: Any = None) -> config.Value | None:
        if entry not in self.entries:
            return on_err
        result = self.instance
        tokens = entry.replace("-", "_").split(".")
        for token in tokens:
            result = getattr(result, token)
        return result

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

    def save(self):
        if self.instance:
            core.json.save(self.instance, core.globals.paths.config, 2)
            core.globals.console.print("[bold]Config: file [green]successfully[/] saved !")
        else:
            core.globals.console.print("[bold]Config: failed to save config. It is not registered !")

    def write(self, entries: dict[str, config.Value]):
        if not self.instance:
            core.globals.console.print("[yellow bold]Config: failed to write entries, config was not registered !")
            core.globals.close()

        for entry, value in entries.items():
            self.set(entry, value)
            core.json.save(self.instance, core.globals.paths.config, 2)
        core.globals.console.print("[bold]Config: entries [green]successfully[/] set !")

    def clean(self):
        if core.globals.paths.config.exists():
            os.remove(core.globals.paths.config)
            core.globals.console.print("[bold]Config: file [green]successfully[/] removed !")
        else:
            core.globals.console.print("[bold]Config: file does not exists !")

    def load(self, path: Path = core.globals.paths.config):
        if not self.instance:
            core.globals.console.print("[bold yellow]Config: failed to load config. It is not registered !")
            return
        if not path.exists():
            core.globals.console.print("[bold yellow]Config: config file not found !")
            return

        data = core.json.load(path)
        try:
            value = type(self.instance).model_validate(data)
            self.instance = value
        except ValidationError:
            core.globals.console.print("[red bold]Config: failed to load config. Json file does not compatible to python model")

    def update(self, info: Update):
        if not self.instance:
            return
        if info.file:
            self.load()
        for preset in info.presets:
            updater = self.presets.get(preset)
            if not updater:
                core.globals.console.print(f"[bold yellow]Config: invalid preset '{preset}'")
            updater(self.instance)
        for k, v in info.overrides.items():
            self.set(k, v)

    def init(self):
        config.register = self.decorator.instance.register
        config.preset = self.decorator.preset.register
        config.get = lambda: self.instance

    def setup(self, update: Update | None = None):
        def recursive(root: core.Model, parent: str, tokens: dict[str, str]):
            for n, f in root.model_fields.items():
                v = getattr(root, n)
                t = type(v)
                if t in (str, int, bool, float):
                    token = f"{parent}.{n}".lstrip(".").replace("_", "-")
                    tokens[token] = f.description or ""
                elif issubclass(t, core.Model):
                    recursive(v, f"{parent}.{n}", tokens)
                else:
                    e = n
                    if parent:
                        e = parent + "." + n
                    raise core.Error(
                        "UnsupportedConfigType",
                        f"Failed to register config !",
                        f"The entry '{e}' is an unsupported type: {t}",
                        f"Only 'str | bool | int | float' are allowed."
                    )

        if self.decorator.instance.registered:
            self.instance = self.decorator.instance.defers[0].func()
            self.entries = {}
            recursive(self.instance, "", self.entries)

        if self.decorator.preset.registered:
            if not self.instance:
                raise utils.RequirementError(
                    "Failed to register config preset: config type was not registered"
                )
            for defer in self.decorator.preset.defers:
                name = defer.args.get("name", defer.func.__name__)
                if name in self.presets:
                    err = utils.ExistsError()
                    err.messages.append(f"Could not register config preset: name '{name}' is already exists")
                    err.details.new(name="name", value=name, desc="Config preset name")
                self.presets[name] = defer.func

        if update:
            self.update(update)

        self.decorator.instance.skip = True
        self.decorator.preset.skip = True
