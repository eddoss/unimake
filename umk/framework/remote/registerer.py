from beartype.typing import Type, Callable

from umk.framework.remote import Interface


class Registerer:
    @property
    def instance(self) -> Interface:
        return self._creator()

    def __init__(self, value: Type | Callable[[], Interface] | None = None):
        self._creator = value


def register(creator):
    return Registerer(creator)


def find(name: str = "") -> Interface | None:
    # See implementation in dot/implementation.py
    raise NotImplemented()


def iterate():
    # See implementation in dot/implementation.py
    raise NotImplemented()
