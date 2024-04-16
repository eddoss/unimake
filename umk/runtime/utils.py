import inspect

from umk import core
from umk.core.typings import Callable, Any, Type


class Defer:
    def __init__(self, func=None, **kwargs):
        self.func: Callable[..., Any] | None = func
        self.args: dict[str, Any] = kwargs

    def __bool__(self):
        return self.func is not None

    def __call__(self, min: int, max: int, _0: Any = None, _1: Any = None, _2: Any = None):
        return call(self.func, min, max, _0, _1, _2)


class SourceError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class FunctionError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class ClassError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class SubclassError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class ExistsError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class NotFoundError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class SignatureError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class RequirementError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


class NotRegisteredError(core.Error):
    def __init__(self, *messages: str, details: core.Properties = None):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = list(messages)
        self.details = details or self.details


def call(func, min: int, max: int, _0: Any = None, _1: Any = None, _2: Any = None):
    sig = len(inspect.signature(func).parameters)
    if sig < min:
        core.globals.error_console.print(
            f"Failed to call '{func.__name__}': arguments valid range is \[min={min}], but {sig} required"
        )
        core.globals.close(-1)
    if max > -1 and sig > max:
        core.globals.error_console.print(
            f"Failed to call '{func.__name__}': arguments valid range is \[min={min} max={max}], but {sig} required"
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


# def cpf(func):
#     """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
#     if inspect.isclass(func):
#         return func
#     result = types.FunctionType(
#         code=func.__code__,
#         globals=func.__globals__,
#         name=func.__name__,
#         argdefs=func.__defaults__,
#         closure=func.__closure__
#     )
#     result = functools.update_wrapper(result, func)
#     result.__kwdefaults__ = func.__kwdefaults__
#     return result


class Decorator(core.Model):
    class OnErrors(core.Model):
        module: core.Error = core.Field(
            default_factory=core.Error,
            description="Error on invalid module"
        )
        subject: core.Error = core.Field(
            default_factory=core.Error,
            description="Error on invalid subject"
        )
        single: core.Error = core.Field(
            default_factory=core.Error,
            description="Error on multiple usage"
        )
        sig: core.Error = core.Field(
            default_factory=core.Error,
            description="Error on invalid signature"
        )
        base: core.Error = core.Field(
            default_factory=core.Error,
            description="Error on invalid base type of the input class"
        )

    class Input(core.Model):
        class Signature(core.Model):
            min: int = core.Field(
                default=0,
                description="Minimum arguments count"
            )
            max: int = core.Field(
                default=-1,
                description="Maximum arguments count"
            )
        subject: str = core.Field(
            default="any",
            description="Which subject must be used this decorator with (class/function/any)"
        )
        base: tuple[Type] | Type | None = core.Field(
            default=None,
            description="Input class base type"
        )
        sig: Signature = core.Field(
            default_factory=Signature,
            description="Signature constraints"
        )

    defers: list[Defer] = core.Field(
        default_factory=list,
        description="Defer function"
    )
    stack: int = core.Field(
        default=2,
        description="Stack level to validate on"
    )
    module: str = core.Field(
        default="",
        description="Which module this decorator is allowed to use in"
    )
    target: str = core.Field(
        default="",
        description="Framework target function name"
    )
    errors: OnErrors = core.Field(
        default_factory=OnErrors,
        description="Errors for each case"
    )
    single: bool = core.Field(
        default=False,
        description="Reject multiple registration"
    )
    skip: bool = core.Field(
        default=False,
        description="Skip registration"
    )
    input: Input = core.Field(
        default_factory=Input,
        description="Input function/class constraints"
    )
    registered: bool = core.Field(
        default=False,
        description="Is register was called ?"
    )

    def init(self, **kwargs):
        pass

    def validate(self, f):
        frame = inspect.stack()[self.stack]
        script = f".unimake/{self.module}.py"
        if not frame.filename.endswith(script):
            raise self.errors.module
        if self.single and self.registered:
            raise self.errors.single
        if self.input.subject == "class":
            if not inspect.isclass(f):
                raise self.errors.subject
            if self.input.base and not issubclass(f, self.input.base):
                raise self.errors.base
        elif self.subject == "function":
            if not inspect.isfunction(f):
                raise self.errors.subject
        sig = len(inspect.signature(f).parameters)
        if sig < self.sig.min:
            raise self.errors.signature
        if self.sig.max > 0:
            if sig > self.sig.max:
                raise self.errors.sig

    @core.overload
    def register(self, f): ...

    @core.overload
    def register(self, f, **kwargs): ...

    def register(self, f=None, **kwargs):
        if f is not None:
            if not self.skip:
                # self.defers.append(Defer(func=cpf(f)))
                self.defers.append(Defer(func=f))
                self.registered = True
            return f

        def dec(fun):
            # parse kwargs
            if not self.skip:
                # self.defers.append(Defer(func=cpf(fun), **kwargs))
                self.defers.append(Defer(func=fun, **kwargs))
                self.registered = True
            return fun

        return dec
