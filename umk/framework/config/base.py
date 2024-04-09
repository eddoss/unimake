from umk import core
from umk.core.typings import TypeVar

Value = str | int | bool | float
ValueTypes = {str, int, bool, float}
Config = core.Model
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
