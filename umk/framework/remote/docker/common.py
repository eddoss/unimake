import os

from umk import globals, core
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface, Events
from umk.framework.system.shell import Shell


class Base(Interface):
    command: list[str] = core.Field(
        default_factory=lambda: ["docker"],
        description="Main shell command",
    ),
    container: str = core.Field(
       description="Target container name",
    )
    sh: str = core.Field(
        description="Default shell (bash, sh, zsh ...)"
    )

    @core.typeguard
    def upload(self, items: dict[str, str], **kwargs):
        me = Events.upload(before=True, instance=self)
        me.data.new("container", self.container, "Container name")
        me.data.new("items.count", len(items), "Items count")
        globals.events.dispatch(me)

        if not items:
            return

        i = 0
        for src, dst in items.items():
            ie = Events.upload_item(before=True, instance=self)
            ie.data.new("container", self.container, "Container name")
            ie.data.new("item.index", i, "Item index")
            ie.data.new("item.src", src, "Item source path")
            ie.data.new("item.dst", dst, "Item destination path")
            globals.events.dispatch(ie)

            cmd = self.command.copy()
            cmd.extend(['container', 'cp', '-q', src, f"{self.container}:{dst}"])
            Shell(command=cmd, name=self.name, log=False).sync()

            ie.name = Events.UPLOAD_ITEM_AFTER
            globals.events.dispatch(ie)

            i += 1

        me.name = Events.UPLOAD_AFTER
        globals.events.dispatch(me)

    @core.typeguard
    def download(self, items: dict[str, str], **kwargs):
        me = Events.download(before=True, instance=self)
        me.data.new("container", self.container, "Container name")
        me.data.new("items.count", len(items), "Items count")
        globals.events.dispatch(me)

        if not items:
            return

        i = 0
        for src, dst in items.items():
            dst = Path(dst).expanduser().resolve().absolute()
            exs = dst.parent.exists()
            ie = Events.download_item(before=True, instance=self)
            ie.data.new("container", self.container, "Container name")
            ie.data.new("item.index", i, "Item index")
            ie.data.new("item.src", src, "Item source path")
            ie.data.new("item.dst", dst, "Item destination path")
            ie.data.new("item.dst.exists", exs, "Whether item destination folder path exists or not")
            globals.events.dispatch(ie)

            if not exs:
                os.makedirs(dst.parent)

            cmd = self.command.copy()
            cmd.extend(['container', 'cp', '-q', f"{self.container}:{src}", dst.as_posix()])
            Shell(command=cmd, name=self.name, log=False).sync()

            i += 1

        me.name = Events.DOWNLOAD_AFTER
        globals.events.dispatch(me)
