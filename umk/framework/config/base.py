from umk import core
from umk.core.typings import TypeVar, Callable, Any
from umk.framework.project import Interface as Project

Value = str | int | bool | float
ValueTypes = {str, int, bool, float}
Interface = core.Model
Implementation = TypeVar("Implementation", bound=Interface)


def register(klass: Implementation):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def preset(
    func: Callable[[Implementation], Any],
    *,
    name: str = ""
):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get() -> Implementation:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
