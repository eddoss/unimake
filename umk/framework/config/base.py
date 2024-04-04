from umk import core
from umk.core.typings import Any, TypeVar

Value = str | int | bool | float
ValueTypes = {str, int, bool, float}


Config = core.Model


class Instance:
    def __init__(self):
        self.entries: dict[str, str] = {}
        self.struct = None

    def set(self, entry: str, value: Value):
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

    def get(self, entry: str, on_err: Any = None) -> None | Value:
        if entry not in self.entries:
            return on_err
        result = self.struct
        tokens = entry.replace("-", "_").split(".")
        for token in tokens:
            result = getattr(result, token)
        return result

    def override(self, *overrides: dict[str, Value]):
        for override in overrides:
            for k, v in override.items():
                self.set(k, v)

    def setup(self):
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


Struct = TypeVar("Struct", bound=core.Model)


def register(factory):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def preset(name: str = ""):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get() -> Struct:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
