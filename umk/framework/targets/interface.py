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

    @abc.abstractmethod
    def object(self, **kwargs) -> core.Object:
        raise NotImplemented()

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
        result = core.Object()
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
        result = core.Object()
        result.type = "Target.Function"
        if self.function:
            sig = inspect.signature(self.function).parameters
            result.new("Name", self.function.__name__, "Function name")
            result.new("Signature", sig, "Function signature")
        else:
            result.new("Name", "", "Function name")
            result.new("Signature", "", "Function signature")
        return result

