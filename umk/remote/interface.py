import abc
from beartype import beartype
from umk.system.environs import OptEnv


class Interface:
    forbidden_names = ("build", "destroy", "up", "down", "shell", "exec")
    @property
    def name(self) -> str:
        """
        Remote environment name.
        """
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        if value in Interface.forbidden_names:
            raise ValueError(f"Given remote environment name is forbidden: '{value}'")
        self._name = value

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

    @abc.abstractmethod
    def build(self, *args, **kwargs):
        """
        Build remote environment.
        """
        ...

    @abc.abstractmethod
    def destroy(self, *args, **kwargs):
        """
        Destroy remote environment.
        """
        ...

    @abc.abstractmethod
    def up(self, *args, **kwargs):
        """
        Start remote environment.
        """
        ...

    @abc.abstractmethod
    def down(self, *args, **kwargs):
        """
        Stop remote environment.
        """
        ...

    @abc.abstractmethod
    def shell(self, *args, **kwargs):
        """
        Open remote environment shell.
        """
        ...

    @abc.abstractmethod
    def execute(self, cmd: list[str], cwd: str = '', env: OptEnv = None):
        """
        Execute command in remote environment.
        """
        ...

    @beartype
    def __init__(self, name: str = "", description: str = "", default: bool = False):
        self._name: str = name
        self._default: bool = default
        self._description = description
