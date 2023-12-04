from beartype.typing import Optional, Type, Callable, Union
from umk.framework.remote import Interface


class Registerer:
    @property
    def instance(self) -> Interface:
        return self._creator()

    def __init__(self, value: Optional[Union[Type, Callable[[], Interface]]] = None):
        self._creator = value


def register(creator):
    return Registerer(creator)


def find(name: str = "") -> Optional[Interface]:
    # See implementation in dot/implementation.py
    raise NotImplemented()


def iterate():
    # See implementation in dot/implementation.py
    raise NotImplemented()
