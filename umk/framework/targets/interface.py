import abc
import inspect

from umk import core
from umk.core.typings import Callable, Any
from umk.framework.system import Shell


class Interface(core.Model):
    name: str = core.Field(
        default="",
        description="Target name"
    )
    label: str = core.Field(
        default="",
        description="Target label"
    )
    description: str = core.Field(
        default="",
        description="Target description"
    )

    def object(self, **kwargs) -> core.Object:
        result = core.Object()
        result.type = "Target"
        result.properties.new(name="Name", value=self.name, desc="Target name")
        result.properties.new(name="Label", value=self.label, desc="Target label")
        result.properties.new(name="Description", value=self.description, desc="Target description")
        return result

    @abc.abstractmethod
    def run(self, **kwargs):
        raise NotImplemented()


class Command(Interface):
    shell: Shell = core.Field(
        default_factory=Shell,
        description="Shell to run"
    )

    def run(self, **kwargs):
        if self.shell.cmd:
            self.shell.sync()

    def object(self) -> core.Object:
        result = super().object()
        result.type = "Target.Command"
        result.properties.new("Command", self.shell.cmd, "Shell command")
        result.properties.new("Workdir", self.shell.workdir or "", "Working directory")
        result.properties.new("Environs", self.shell.environs or "", "Environment variables")
        return result


class Function(Interface):
    function: Callable[[], Any] = core.Field(
        default=None,
        description="Function to run"
    )

    def run(self, **kwargs):
        if self.function:
            self.function()

    def object(self) -> core.Object:
        result = super().object()
        result.type = "Target.Function"
        if self.function:
            sig = inspect.signature(self.function).parameters
            result.properties.new("Name", self.function.__name__, "Function name")
            result.properties.new("Signature", sig, "Function signature")
        else:
            result.properties.new("Name", "", "Function name")
            result.properties.new("Signature", "", "Function signature")
        return result


def register(func):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def function(name: str = "", label: str = "", description: str = ""):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()

