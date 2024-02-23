from umk import globals, core
from umk.framework.remote.docker import common
from umk.framework.remote.interface import Events
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell


class Container(common.Base):
    container: str = core.Field(
        default="",
        description="Docker container name"
    )

    @core.typeguard
    def __init__(
        self,
        name: str = "",
        description: str = "Docker container environment",
        default: bool = False,
        container: str = "",
        shell: str = "sh",
    ):
        super().__init__(
            name=name,
            default=default,
            description=description,
            command=["docker"],
            sh=shell
        )
        self.container = container

    def _register_properties(self):
        super()._register_properties()
        self._properties.add("container")

    @core.typeguard
    def shell(self, *args, **kwargs):
        e = Events.shell(before=True, instance=self)
        e.data.new("container", self.container, "Container name")
        e.data.new("shell", self.container, "Shell name")
        if kwargs:
            e.data.new("extra_args", kwargs)
        globals.events.dispatch(e)

        command = self.command.copy()
        command.extend(["exec", "-i", "-t", self.container, self.sh])
        Shell(command, name=self.name).sync()

        e.name = Events.SHELL_AFTER
        globals.events.dispatch(e)

    @core.typeguard
    def execute(self, cmd: list[str], cwd: str = "", env: envs.Optional = None, *args, **kwargs):
        e = Events.execute(before=True, instance=self)
        e.data.new("container", self.container, "Container name")
        e.data.new("shell", self.container, "Shell name")
        e.data.new("command", cmd, "Command to execute")
        e.data.new("workdir", cwd, "Working directory")
        e.data.new("environs", env, "Environment variables")
        if kwargs:
            e.data.new("extra_args", kwargs)
        globals.events.dispatch(e)

        command = self.command.copy()
        command.extend(["exec", "-t"])
        if cwd:
            command.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                command.extend(["-e", f"{k}={v}"])
        command.append(self.container)
        command.extend(cmd)
        Shell(command, name=self.name).sync()

        e.name = Events.EXECUTE_AFTER
        globals.events.dispatch(e)
