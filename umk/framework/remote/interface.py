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
        # for field in type(self).__fields__:
        for field in self.model_fields:
            yield core.Property.from_field(self, field)

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

    def __hash__(self) -> int:
        return hash(self.name)


class Events:
    @staticmethod
    def build(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.build.before' / 'remote.build.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_BUILD if before else globals.EventNames.REMOTE_BUILD)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def destroy(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.destroy.before' / 'remote.destroy.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_DESTROY if before else globals.EventNames.REMOTE_DESTROY)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def up(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.up.before' / 'remote.up.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_UP if before else globals.EventNames.REMOTE_UP)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def down(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.down.before' / 'remote.down.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_DOWN if before else globals.EventNames.REMOTE_DOWN)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def execute(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.execute.before' / 'remote.execute.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_EXECUTE if before else globals.EventNames.REMOTE_EXECUTE)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def shell(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.shell.before' / 'remote.shell.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_SHELL if before else globals.EventNames.REMOTE_SHELL)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def upload(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.upload.before' / 'remote.upload.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_UPLOAD if before else globals.EventNames.REMOTE_UPLOAD)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def upload_item(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.upload.item.before' / 'remote.upload.item.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_UPLOAD_ITEM if before else globals.EventNames.REMOTE_UPLOAD_ITEM)
        result.data = data if data else core.EventData()
        result.data.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def download(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.download.before' / 'remote.download.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_DOWNLOAD if before else globals.EventNames.REMOTE_DOWNLOAD)
        result.data = data if data else core.EventData()
        result.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result

    @staticmethod
    def download_item(before: bool, instance: Interface, data: core.EventData | None = None) -> core.Event:
        """
        Creates 'remote.download.item.before' / 'remote.download.item.after' event.
        """
        result = core.Event(name=globals.EventNames.REMOTE_DOWNLOAD_ITEM if before else globals.EventNames.REMOTE_DOWNLOAD_ITEM)
        result.data = data if data else core.EventData()
        result.new("instance", instance, "Remote interface instance")
        result.data.new("state", "before" if before else "after", "Is action at the beginning")
        return result
