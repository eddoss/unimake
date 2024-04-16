from umk.core.typings import Model

Value = str | int | bool | float
Interface = Model


def register(klass):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def preset(*, name: str = ""):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
