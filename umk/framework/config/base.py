import copy

from umk.core.typings import Any, TypeVar, Type

Value = str | int | bool | float
ValidValueTypes = [str, int, bool, float]


class Entry:
    def __init__(self, description: str, name: str = "", default: Value = None):
        self.name = name
        self.default = default
        self.description = description
        self.property = property(fget=lambda inst: self.default, doc=description)


class Interface:
    def __init__(self):
        self._entries: dict[str, Entry] = {}

    def set(self, name: str, value: Value):
        field = self._entries.get(name)
        if not field:
            # TODO Raise error for this case
            raise NameError(f"Config: field '{name}' does not exists")
        field.value = value

    def get(self, name: str, err: Any = None) -> None | Value:
        field = self._entries.get(name)
        if field:
            return field.default
        return err

    def entry(self, name: str) -> None | Entry:
        return self._entries.get(name)

    def apply(self, preset: dict[str, Value]):
        for k, v in preset.items():
            self.set(k, v)

    def setup(self):
        cls = type(self)
        for k in list(cls.__dict__.keys()):
            v = copy.deepcopy(cls.__dict__[k])
            if not isinstance(v, Entry):
                continue
            self._entries[v.name or k.replace("_", "-")] = v
            delattr(cls, k)
            setattr(cls, k, v.property)

    def __validate_name(self, name: str) -> str:
        # TODO Raise error for this case
        raise NameError(f"Config: invalid variable name '{name}'")

    def __validate_variable(self, name: str):
        # TODO Raise error for this case
        raise NameError(f"Config: invalid variable name '{name}'")


Implementation = TypeVar("Implementation", bound=Interface)


def register(factory):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get() -> Implementation:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def entry(name: str) -> Entry:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def string(name: str) -> str:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def integer(name: str) -> int:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def boolean(name: str) -> bool:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def floating(name: str) -> float:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def array(name: str, t: Type = str) -> list:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def preset(name: str = "") -> float:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
