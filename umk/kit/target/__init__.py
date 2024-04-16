from beartype.typing import Generator

from umk.framework.target.interface import Interface
from umk.framework.target.interface import Function
from umk.framework.target.interface import Command

from umk.framework.target.packages import SystemPackages

from umk.framework.target.golang import GolangBinary
from umk.framework.target.golang import GolangMod


def run(*names: str):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def iterate() -> Generator[Interface, None, None]:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def custom(klass):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def function(name: str = "", label: str = "", description: str = ""):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def command(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


class go:
    @staticmethod
    def binary(debug=True):
        # See implementation in runtime.Instance.implementation()
        raise NotImplemented()

    @staticmethod
    def mod(func):
        # See implementation in runtime.Instance.implementation()
        raise NotImplemented()


def packages(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
