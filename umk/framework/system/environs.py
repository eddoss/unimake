import os

from umk import core


class EnvironmentNotExistsError(Exception):
    def __init__(self, name: str, message: str = ""):
        self.name = name
        self.message = message

    def __str__(self):
        if self.message:
            return f"Environment '{self.name}' is required. {self.message}"
        else:
            return f"Environment '{self.name}' is required"


class Environs(dict):
    @core.typeguard
    def __init__(self, inherit=True, **var):
        super().__init__()
        if inherit:
            for name, value in os.environ.items():
                self[name] = value
        for k, v in var.items():
            self[k] = v

    @core.typeguard
    def prepend(self, name: str, *values: str) -> None:
        nonempty = filter(None, values)
        value = os.pathsep.join(nonempty)
        if name in self and self[name]:
            value += os.pathsep + self[name]
        self[name] = value

    @core.typeguard
    def append(self, name: str, *values: str) -> None:
        nonempty = filter(None, values)
        appended = os.pathsep.join(nonempty)
        if name in self and self[name]:
            appended = f'{self[name]}{os.pathsep}{appended}'
        self[name] = appended

    @core.typeguard
    def require(self, name: str, message: str = ""):
        if name in self:
            return
        raise EnvironmentNotExistsError(name=name, message=message)


OptEnv = None | Environs
