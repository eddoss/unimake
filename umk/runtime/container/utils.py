import inspect

from umk import core
from umk.core.typings import Callable, Any


class Defer:
    def __init__(self, func=None, **kwargs):
        self.func: Callable[..., Any] | None = func
        self.args: dict[str, Any] = kwargs

    def __bool__(self):
        return self.func is not None

    def __call__(self, min: int, max: int, _0: Any = None, _1: Any = None, _2: Any = None):
        return call(self.func, min, max, _0, _1, _2)


class SourceModuleError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


class NotFunctionError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


class NotClassError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


class NotSubclassError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


class AlreadyExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


class InvalidArgumentsCountError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))


def validate_source_module(*, script: str, stack: int, messages: list[str], properties: core.Properties = None):
    frame = inspect.stack()[stack]
    name = f".unimake/{script}.py"
    if not frame.filename.endswith(name):
        err = SourceModuleError()
        err.details = properties or core.Properties()
        err.messages = [m.replace("@script", name) for m in messages]
        raise err


def validate_only_function(*, factory, messages: list[str], properties: core.Properties = None):
    if not inspect.isfunction(factory):
        err = NotFunctionError()
        err.details = properties or core.Properties()
        err.messages = messages
        raise err


def validate_only_class(*, factory, messages: list[str], properties: core.Properties = None):
    if not inspect.isclass(factory):
        err = NotClassError()
        err.details = properties or core.Properties()
        err.messages = messages
        raise err


def validate_only_subclass(*, obj, base, messages: list[str], properties: core.Properties = None):
    if not issubclass(type(obj), base):
        err = NotSubclassError()
        err.details = properties or core.Properties()
        err.messages = messages
        raise err


def raise_already_exists(*, messages: list[str], properties: core.Properties = None):
    err = AlreadyExistsError()
    err.details = properties or core.Properties()
    err.messages = messages
    raise err


def call(func, min: int, max: int, _0: Any = None, _1: Any = None, _2: Any = None):
    sig = len(inspect.signature(func).parameters)
    if sig < min or sig > max:
        core.globals.error_console.print(
            f"Failed to call '{func.__name__}': arguments valid range is \[min={min} max={max}], but {sig} required w"
        )
        core.globals.close(-1)
    if sig == 0:
        return func()
    if sig == 1:
        return func(_0)
    elif sig == 2:
        return func(_0, _1)
    elif sig == 3:
        return func(_0, _1, _2)
