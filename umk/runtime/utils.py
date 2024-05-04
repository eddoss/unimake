import inspect
from collections import OrderedDict

from umk import core
from umk.core.typings import Callable, Any, Type, Mapping


class SignatureArgument(core.Model):
    description: str = core.Field("", description="Argument description")
    # provider: Callable[..., Any] = core.Field(None, description="Value provider")


class Signature(core.Model):
    required: OrderedDict[str, SignatureArgument] = core.Field(default_factory=dict, description="Required arguments (passed by position)")
    optional: dict[str, SignatureArgument] = core.Field(default_factory=dict, description="Optional arguments (passed by name)")

    def ok(self, func):
        sig = inspect.signature(func).parameters
        if self.required:
            if len(sig) < len(self.required):
                raise SignatureError(self, sig)
            for req, inp in zip(self.required, sig):
                if req != inp:
                    raise SignatureError(self, sig)
        # for inp in sig:
        #     if inp in self.required:
        #         continue
            # if inp not in self.optional:
            #     core.globals.console.print(f"[yellow bold]Unknown parameter '{inp}', pass None")

    def call(self, func, args: dict[str, Any]):
        sig = inspect.signature(func).parameters
        kwargs = {}
        unknown = {}
        for name in sig:
            if name in self.required or name in self.optional:
                kwargs[name] = args[name]
            else:
                unknown[name] = None
                core.globals.console.print(f"[yellow underline bold]unknown parameters '{name}', pass None")
        return func(**kwargs, **unknown)


class Defer:
    def __init__(self, func=None, **kwargs):
        self.func: Callable[..., Any] | None = func
        self.args: dict[str, Any] = kwargs
        self.sig: dict[str, SignatureArgument] = {}

    def __bool__(self):
        return self.func is not None

    def __call__(self, min: int, max: int, _0: Any = None, _1: Any = None, _2: Any = None):
        p: dict[str, Any] = {}
        return call(self.func, min, max, _0, _1, _2)

    def call(self, sg):
        sig = inspect.signature(self.func).parameters
        kwargs = {}
        for name in sig:
            if name in sg.required:
                continue
            value = None
            info = sg.optional.get(name)
            if name:
                value = info.provider()
            kwargs[name] = value
        args = [req.provider() for req in sg.required.values()]
        self.func(*args, **kwargs)


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
    def __init__(self, req: Signature, inp: Mapping[str, inspect.Parameter]):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Invalid signature."]

        if req.required:
            self.messages.append("required:")
            for name, r in req.required.items():
                self.messages.append(
                    f" - '{name}' {r.description}"
                )
        if req.optional:
            self.messages.append("optional:")
            for name, o in req.optional.items():
                self.messages.append(
                    f" - '{name}' {o.description}"
                )
        if not req.required and not req.optional:
            self.messages.append("No parameters required")

        # if req.required:
        #     self.messages = [
        #         f"Required arguments:",
        #         f" - {}
        #     ]
        # if req:
        #     f" - ({' ,'.join(req.required)}, {' ,'.join(req.optional)}) -> Any",
        # elif req.required:
        #     self.messages = [
        #         f"Required signature one of:",
        #         f" - ({' ,'.join(req.required)}) -> Any",
        #     ]
        # self.details = details or self.details


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
        subject: str = core.Field(
            default="any",
            description="Which subject must be used this decorator with (class/function/any)"
        )
        base: tuple[Type] | Type | None = core.Field(
            default=None,
            description="Input class base type"
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
    sig: Signature = core.Field(
        default_factory=Signature,
        description="Signature constraints"
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
        if self.single and self.registered and self.skip:
            raise self.errors.single
        if self.input.subject == "class":
            if not inspect.isclass(f):
                raise self.errors.subject
            if self.input.base and not issubclass(f, self.input.base):
                raise self.errors.base
        elif self.input.subject == "function":
            if not inspect.isfunction(f):
                raise self.errors.subject
        self.sig.ok(f)

    @core.overload
    def register(self, f): ...

    @core.overload
    def register(self, f, **kwargs): ...

    def register(self, f=None, **kwargs):
        if f is not None:
            if not self.skip:
                # self.defers.append(Defer(func=cpf(f)))
                self.validate(f)
                self.defers.append(Defer(func=f))
                self.registered = True
            return f

        def dec(fun):
            # parse kwargs
            if not self.skip:
                # self.defers.append(Defer(func=cpf(fun), **kwargs))
                self.validate(fun)
                self.defers.append(Defer(func=fun, **kwargs))
                self.registered = True
            return fun

        return dec
