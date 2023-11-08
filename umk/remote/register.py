from beartype.typing import Optional
from beartype import beartype
from umk import exceptions
from .interface import Interface


Registered: dict[str, Interface] = {}


@beartype
def register(creator):
    global Registered
    interface: Interface = creator()
    if interface.name in Registered:
        raise exceptions.RemoteExistsError(f"Remote '{interface.name}' is already registered")
    dr = find()
    if interface.default and dr:
        raise exceptions.DefaultRemoteExistsError(f"Default remote is already set: {dr.name}")
    Registered[interface.name] = interface
    return creator


def find(name: str = "") -> Optional[Interface]:
    global Registered
    if not name:
        for remote in Registered.values():
            if remote.default:
                return remote
    else:
        return Registered.get(name)


def iterate():
    global Registered
    for _, rem in Registered.items():
        yield rem
