from umk.core.typings import Generator

from umk import core
from umk.core.typings import TypeVar
from umk.framework import utils
from umk.framework.filesystem import AnyPath, OptPath
from umk.framework.system import OptEnv


class Interface(core.Model):
    name: str = core.Field(
        default="",
        description="Remote environment name",
    )
    description: str = core.Field(
        default="",
        description="Remote environment description",
    )
    default: bool = core.Field(
        default=False,
        description="Whether this remote environment are default or not",
    )

    def properties(self) -> Generator[core.Property, None, None]:
        """
        Remote environment properties
        """
        for name in self.model_fields:
            result = self.property(name)
            for prop in result:
                yield prop

    def property(self, name: str) -> list[core.Property]:
        field = self.model_fields[name]
        if not field.repr:
            return []
        return [
            core.Property(
                name=name,
                description=field.description,
                value=getattr(self, name)
            )
        ]

    def build(self, **kwargs):
        """
        Build remote environment.
        """
        self.__not_implemented()

    def destroy(self, **kwargs):
        """
        Destroy remote environment.
        """
        self.__not_implemented()

    def up(self, **kwargs):
        """
        Start remote environment.
        """
        self.__not_implemented()

    def down(self, **kwargs):
        """
        Stop remote environment.
        """
        self.__not_implemented()

    def shell(self, **kwargs):
        """
        Open remote environment shell.
        """
        self.__not_implemented()

    @core.typeguard
    def execute(self, cmd: list[AnyPath], cwd: OptPath = None, env: OptEnv = None, **kwargs):
        """
        Execute command in remote environment.
        """
        self.__not_implemented()

    @core.typeguard
    def upload(self, items: dict[AnyPath, AnyPath], **kwargs):
        """
        Upload given paths to remote environment.
        """
        self.__not_implemented()

    @core.typeguard
    def download(self, items: dict[AnyPath, AnyPath], **kwargs):
        """
        Download given paths from remote environment.
        """
        self.__not_implemented()

    def __not_implemented(self):
        core.globals.console.print(
            f"[bold]The '{self.name}' remote environment has no '{utils.caller(2)}' function. "
            f"It`s must be managed outside of this tool."
        )

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self):
        return f"umk.remote.Interface(name='{self.name}', description='{self.description}')"


Implementation = TypeVar("Implementation", bound=Interface)


def register(factory):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def find(name: str = "") -> Implementation:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def iterate():
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()
