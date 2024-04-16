from umk.framework.remote.docker import Compose as DockerCompose
from umk.framework.remote.docker import Container as DockerContainer
from umk.framework.remote.docker import Login as DockerLogin
from umk.framework.remote.interface import Interface
from umk.framework.remote.ssh import SecureShell

__all__ = [
    "Interface",
    "DockerContainer",
    "DockerCompose",
    "DockerLogin",
    "SecureShell",
]


class docker:
    @staticmethod
    def compose(factory):
        # See implementation in runtime.Instance.implementation()
        raise NotImplemented()

    @staticmethod
    def container(factory):
        # See implementation in runtime.Instance.implementation()
        raise NotImplemented()


def ssh(factory):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def custom():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def find(name: str, on_err=None):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def default(on_err=None):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def iterate():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
