import inspect

from umk import core
from umk.core.typings import Type, Callable
from umk.framework.remote import Interface


class RemoteInstanceRegisterError(core.Error):
    def __init__(self, factory_type: str, factory_name: str, position: str):
        super().__init__(name=type(self).__name__)
        self.messages = [
            "The decorator 'umk.remote.register' must be used with functions "
            "(or classes) that returns 'umk.remote.Interface' implementation."
        ]
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="type", value=factory_type, desc="Remote environment factory type")
        self.details.new(name="at", value=position, desc="File position")


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
        raise RemoteInstanceRegisterError(
            factory_type="function" if inspect.isfunction(self._creator) else "class",
            factory_name=self._name,
            position=f"{self._frame.filename}:{self._frame.lineno}"
        )


def register(creator):
    return Registerer(creator, inspect.stack()[1])


def find(name: str = "") -> Interface | None:
    # See implementation in dot/implementation.py
    raise NotImplemented()


def iterate():
    # See implementation in dot/implementation.py
    raise NotImplemented()
