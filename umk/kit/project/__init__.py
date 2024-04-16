# base
from umk.framework.project.base import Contributor
from umk.framework.project.base import Info
from umk.framework.project.base import Layout
from umk.framework.project.base import Interface
from umk.framework.project.base import Scratch

# golang
from umk.framework.project.golang import Golang
from umk.framework.project.golang import GolangLayout


def custom(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def empty(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def golang(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def releaser(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def release():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
