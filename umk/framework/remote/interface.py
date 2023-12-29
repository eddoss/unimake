from beartype.typing import Generator

from umk import core, globals
from umk.framework import utils
from umk.framework.system import environs as envs


class Interface(core.Object):
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
        for name in self._properties:
            yield core.Property.from_field(self, name)

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
    def execute(self, cmd: list[str], cwd: str = '', env: envs.Optional = None, **kwargs):
        """
        Execute command in remote environment.
        """
        self.__not_implemented()

    @core.typeguard
    def upload(self, items: dict[str, str], **kwargs):
        """
        Upload given paths to remote environment.
        """
        self.__not_implemented()

    @core.typeguard
    def download(self, items: dict[str, str], **kwargs):
        """
        Download given paths from remote environment.
        """
        self.__not_implemented()

    def __not_implemented(self):
        globals.console.print(
            f"[bold]The '{self.name}' remote environment has no '{utils.caller(2)}' function. "
            f"It`s must be managed outside of this tool."
        )

    def _register_properties(self):
        self._properties.add("name")
        self._properties.add("description")
        self._properties.add("default")

    def __hash__(self) -> int:
        return hash(self.name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._properties: set[str] = set()
        self._register_properties()


class Events:
    BUILD_BEFORE = "remote.build.before"
    BUILD_AFTER = "remote.build.after"

    DESTROY_BEFORE = "remote.destroy.before"
    DESTROY_AFTER = "remote.destroy.after"

    UP_BEFORE = "remote.up.before"
    UP_AFTER = "remote.up.after"

    DOWN_BEFORE = "remote.down.before"
    DOWN_AFTER = "remote.down.after"

    EXECUTE_BEFORE = "remote.execute.before"
    EXECUTE_AFTER = "remote.execute.after"

    SHELL_BEFORE = "remote.shell.before"
    SHELL_AFTER = "remote.shell.after"

    UPLOAD_BEFORE = "remote.upload.before"
    UPLOAD_AFTER = "remote.upload.after"
    UPLOAD_ITEM_BEFORE = "remote.upload.item.before"
    UPLOAD_ITEM_AFTER = "remote.upload.item.after"

    DOWNLOAD_BEFORE = "remote.download.before"
    DOWNLOAD_AFTER = "remote.download.after"
    DOWNLOAD_ITEM_BEFORE = "remote.download.item.before"
    DOWNLOAD_ITEM_AFTER = "remote.download.item.after"

    @staticmethod
    def build(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.build.before' / 'remote.build.after' event.
        """
        result = core.Event(name=Events.BUILD_BEFORE if before else Events.BUILD_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def destroy(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.destroy.before' / 'remote.destroy.after' event.
        """
        result = core.Event(name=Events.DESTROY_BEFORE if before else Events.DESTROY_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def up(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.up.before' / 'remote.up.after' event.
        """
        result = core.Event(name=Events.UP_BEFORE if before else Events.UP_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def down(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.down.before' / 'remote.down.after' event.
        """
        result = core.Event(name=Events.DOWN_BEFORE if before else Events.DOWN_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def execute(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.execute.before' / 'remote.execute.after' event.
        """
        result = core.Event(name=Events.EXECUTE_BEFORE if before else Events.EXECUTE_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def shell(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.shell.before' / 'remote.shell.after' event.
        """
        result = core.Event(name=Events.SHELL_BEFORE if before else Events.SHELL_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def upload(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.upload.before' / 'remote.upload.after' event.
        """
        result = core.Event(name=Events.UPLOAD_BEFORE if before else Events.UPLOAD_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def upload_item(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.upload.item.before' / 'remote.upload.item.after' event.
        """
        result = core.Event(name=Events.UPLOAD_ITEM_BEFORE if before else Events.UPLOAD_ITEM_AFTER)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def download(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.download.before' / 'remote.download.after' event.
        """
        result = core.Event(name=Events.DOWNLOAD_BEFORE if before else Events.DOWNLOAD_AFTER)
        result.data = data if data else core.EventData()
        result.new("instance", instance, "Remote interface instance")
        return result

    @staticmethod
    def download_item(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.download.item.before' / 'remote.download.item.after' event.
        """
        result = core.Event(name=Events.DOWNLOAD_ITEM_BEFORE if before else Events.DOWNLOAD_ITEM_AFTER)
        result.data = data if data else core.EventData()
        result.new("instance", instance, "Remote interface instance")
        return result
