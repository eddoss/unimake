import abc
import inspect

from umk import core
from umk.core.typings import Callable, Any
from umk.framework.system.shell import Shell


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
    function: Callable[..., Any] = core.Field(
        default=None,
        description="Function to run"
    )

    def run(self, **kwargs):
        if self.function:
            sig = len(inspect.signature(self.function).parameters)
            if sig == 0:
                self.function()
            elif sig == 1:
                self.function(kwargs.get("c"))
            else:
                self.function(kwargs.get("c"), kwargs.get("p"))

    def object(self) -> core.Object:
        result = super().object()
        result.type = "Target.Function"
        return result


