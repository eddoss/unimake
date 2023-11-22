from textwrap import dedent
from beartype import beartype
from beartype.typing import Any, Optional
from umk.globals import Global
from umk.system.environs import OptEnv
from umk.system import code


class Property:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        name = value.strip()
        if name == '':
            raise ValueError(f"Remote environment property name should not be empty: '{name}'")
        self._name = name

    @property
    def value(self) -> Optional[Any]:
        return self._value

    @value.setter
    @beartype
    def value(self, value: Optional[Any]):
        self._value = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    @beartype
    def description(self, value: str):
        self._description = dedent(value)

    @beartype
    def __init__(self, name: str, description: str = '', value: Any = None):
        self._name = name
        self.name = name
        self._value = value
        self._description = description


class Interface:
    @property
    def name(self) -> str:
        """
        Remote environment name.
        """
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        name = value.strip()
        if name == '':
            raise ValueError(f"Given remote environment name is forbidden: '{name}'")
        self._name = name

    @property
    def description(self) -> str:
        """
        Remote environment description.
        """
        return self._description

    @description.setter
    @beartype
    def description(self, value: str):
        self._description = value

    @property
    def default(self) -> bool:
        """
        Whether this remote environment are default or not.
        """
        return self._default

    @default.setter
    @beartype
    def default(self, value: bool):
        self._default = value

    @property
    def details(self) -> dict[str, Property]:
        """
        Remote environment detailed information
        """
        return self._details

    def build(self, *args, **kwargs):
        """
        Build remote environment.
        """
        self.__not_implemented()

    def destroy(self, *args, **kwargs):
        """
        Destroy remote environment.
        """
        self.__not_implemented()

    def up(self, *args, **kwargs):
        """
        Start remote environment.
        """
        self.__not_implemented()

    def down(self, *args, **kwargs):
        """
        Stop remote environment.
        """
        self.__not_implemented()

    def shell(self, *args, **kwargs):
        """
        Open remote environment shell.
        """
        self.__not_implemented()

    def execute(self, cmd: list[str], cwd: str = '', env: OptEnv = None, *args, **kwargs):
        """
        Execute command in remote environment.
        """
        self.__not_implemented()

    def upload(self, paths: dict[str, str], *args, **kwargs):
        """
        Upload given paths to remote environment.
        """
        self.__not_implemented()

    def download(self, paths: dict[str, str], *args, **kwargs):
        """
        Download given paths from remote environment.
        """
        self.__not_implemented()

    def __not_implemented(self):
        Global.console.print(
            f"[bold]The '{self.name}' remote environment has no '{code.caller(2)}' function. "
            f"It`s must be managed outside of this tool."
        )

    @beartype
    def __init__(self, name: str = "", description: str = "", default: bool = False):
        self._name: str = name
        self._default: bool = default
        self._description = description
        self._details: dict[str, Property] = {}
