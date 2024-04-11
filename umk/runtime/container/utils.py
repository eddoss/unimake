from umk.core.typings import Callable, Any


class Defer:
    def __init__(self, func=None, **kwargs):
        self.func: Callable[..., Any] | None = func
        self.args: dict[str, Any] = kwargs

    def __bool__(self):
        return self.func is not None
