import inspect

import rich.table

from umk import core
from umk.framework.remote import Interface
from umk.typing import Type, Callable


class Registerer:
    @property
    def instance(self) -> Interface:
        imlp = self._creator()
        self.validate(imlp)
        if not imlp.name:
            imlp.name = self._name
        return imlp

    def __init__(self, value: Type | Callable[[], Interface] | None = None, frame=None):
        self._creator = value
        self._name = value.__name__
        self._frame: inspect.FrameInfo = frame

    def validate(self, imlp):
        if issubclass(type(imlp), Interface):
            return
        err = core.Error()
        err["function" if inspect.isfunction(self._creator) else "class"] = f"'{self._name}'"
        err["at"] = f"{self._frame.filename}:{self._frame.lineno}"
        err.message = f"The decorator 'umk.remote.register' must be used with functions (or classes) " \
                      f"that returns 'umk.remote.Interface' implementation."
        raise err


def register(creator):
    return Registerer(creator, inspect.stack()[1])


def find(name: str = "") -> Interface | None:
    # See implementation in dot/implementation.py
    raise NotImplemented()


def iterate():
    # See implementation in dot/implementation.py
    raise NotImplemented()
