import inspect


def caller(level: int = 1) -> str:
    stack = inspect.stack()
    caller_info = stack[level]
    name = caller_info.function
    return name
