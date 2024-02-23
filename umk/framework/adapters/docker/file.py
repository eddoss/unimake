import io
from datetime import timedelta

from beartype.typing import TextIO, Optional, Any

from umk import core

from umk.framework.system import User as OSUser


class Instruction(core.Object):
    def write(self, buffer: TextIO):
        pass


class Commentable(core.Object):
    comment: list[str] = core.Field(
        description="Instruction comment lines",
        default_factory=list,
    )
    space: int = core.Field(
        description="Instruction pre-space count",
        default=0,
    )

    def write(self, buffer: TextIO):
        if self.space or self.comment:
            buffer.write("\n")
        if self.comment:
            for line in self.comment:
                text = f"# {line}\n"
                buffer.write(text)


class Add(Commentable):
    """
    Add local or remote files and directories.
    """
    src: str = ""
    dst: str = ""
    chown: Optional[OSUser] = None
    chmod: Optional[int] = None
    checksum: Optional[str] = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = "ADD"
        if self.chown is not None:
            text += f" --chown={self.chown.name}"
            if self.chown.group.name:
                text += f":{self.chown.group.name}"
        if self.chmod is not None:
            text += f" --chmod={self.chmod}"
        if self.checksum is not None:
            text += f" --checksum={self.checksum}"
        if text:
            text += " "
        text += f"{self.src} {self.dst}\n"
        buffer.write(text)


class Arg(Commentable):
    """
    Use build-time variables.
    """
    name: str
    value: Any = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"ARG {self.name}"
        if self.value is not None:
            text += f"={self.value}"
        text += "\n"
        buffer.write(text)


class Cmd(Commentable):
    """ 
    Specify default commands.
    """
    args: list[str] = core.Field(default_factory=list)

    def __init__(self, *args: str):
        super().__init__()
        self.args = list(args)

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"CMD {self.args}\n"
        buffer.write(text)


class Copy(Commentable):
    """ 
    Copy files and directories.
    """
    src: str = ""
    dst: str = ""
    chown: Optional[OSUser] = None
    chmod: Optional[int] = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = "COPY"
        if self.chown is not None:
            text += f" --chown={self.chown.name}"
            if self.chown.group.name:
                text += f":{self.chown.group.name}"
        if self.chmod is not None:
            text += f" --chmod={self.chmod}"
        if text:
            text += " "
        text += f"{self.src} {self.dst}\n"
        buffer.write(text)


class Entrypoint(Commentable):
    """
    Specify default executable.
    """
    args: list[str] = core.Field(default_factory=list)

    def __init__(self, args: list[str], **kwargs):
        super().__init__(**kwargs)
        self.args = args

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"ENTRYPOINT {self.args}\n"
        buffer.write(text)


class Env(Commentable):
    """
    Set environment variables.
    """
    name: str
    value: Any

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"ENV {self.name}={self.value}\n"
        buffer.write(text)


class Expose(Commentable):
    """
    Describe which ports your application is listening on.
    """
    port: int
    protocol: Optional[str] = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"EXPOSE {self.port}"
        if self.protocol:
            text += f"/{self.protocol}"
        text += "\n"
        buffer.write(text)


class From(Commentable):
    """
    Create a new build stage from a base image.
    """
    image: str
    platform: Optional[str] = None
    alias: Optional[str] = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"FROM"
        if self.platform:
            text += f" --platform={self.platform}"
        text += f" {self.image}"
        if self.alias:
            text += f" AS {self.alias}"
        text += "\n"
        buffer.write(text)


class Healthcheck(Commentable):
    """
    Check a container's health on startup.
    """
    interval: Optional[timedelta] = None
    timeout: Optional[timedelta] = None
    start_period: Optional[timedelta] = None
    start_interval: Optional[timedelta] = None
    retries: Optional[int] = None
    command: list[str] = core.Field(default_factory=list)

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"HEALTHCHECK"
        if self.interval:
            text += f" --interval={self.interval.total_seconds()}s"
        if self.timeout:
            text += f" --timeout={self.timeout.total_seconds()}s"
        if self.start_period:
            text += f" --start_period={self.start_period.total_seconds()}s"
        if self.start_interval:
            text += f" --start_interval={self.start_interval.total_seconds()}s"
        if self.retries:
            text += f" --retries={self.retries}"
        cmd = "NONE"
        if self.command:
            cmd = " ".join(self.command)
        text += f" CMD {cmd}\n"
        buffer.write(text)


class Label(Commentable):
    """
    Add metadata to an image.
    """
    items: dict[str, str] = core.Field(default_factory=dict)

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = "LABEL"
        for name, value in self.items.items():
            text += f' "{name}"="{value}"'
        text += "\n"
        buffer.write(text)


class Maintainer(Commentable):
    """
    Specify the author of an image.
    """
    name: str

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"MAINTAINER {self.name}\n"
        buffer.write(text)
        pass


class OnBuild(Commentable):
    """
    Specify instructions for when the image is used in a build.
    """
    instruction: Commentable = core.Field(kw_only=False)

    def write(self, buffer: TextIO):
        super().write(buffer)
        buf = io.StringIO()
        self.instruction.write(buf)
        ins = buf.getvalue().lstrip()
        text = f"ONBUILD {ins}\n"
        buffer.write(text)


class Run(Commentable):
    """
    Execute build commands.
    """
    commands: list[str] = core.Field(default_factory=list)

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = "RUN"
        if len(self.commands) == 1:
            text += f" {self.commands[0]}"
        else:
            text += "<<EOF\n"
            for cmd in self.commands:
                text += f"{cmd}\n"
            text += "EOF\n"
        buffer.write(text)


class Shell(Commentable):
    """
    Set the default shell of an image.
    """
    args: list[str] = core.Field(default_factory=list)

    def __init__(self, *args: str):
        super().__init__()
        self.args = list(args)

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"SHELL {self.args}\n"
        buffer.write(text)


class StopSignal(Commentable):
    """
    Specify the system call signal for exiting a container.
    """
    signal: int

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"STOPSIGNAL {self.signal}\n"
        buffer.write(text)


class User(Commentable):
    """
    Set user and group ID.
    """
    user: str
    group: Optional[str] = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"USER {self.user}"
        if self.group:
            text += f":{self.group}"
        text += "\n"
        buffer.write(text)


class Volume(Commentable):
    """
    Create volume mounts.
    """
    path: str

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"VOLUME {self.path}\n"
        buffer.write(text)


class Workdir(Commentable):
    """
    Change working directory.
    """
    path: str

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = f"WORKDIR {self.path}\n"
        buffer.write(text)


class Comment(Instruction):
    """
    Comment lines.
    """
    lines: list[str] = core.Field(
        description="Comment lines",
        default_factory=list,
    )

    def write(self, buffer: TextIO):
        super().write(buffer)
        for line in self.lines:
            buffer.write(f"# {line}\n")


class Space(Instruction):
    """
    Comment lines.
    """
    count: int = core.Field(
        description="Empty lines count",
        default=1,
    )

    def write(self, buffer: TextIO):
        super().write(buffer)
        buffer.write(max(1, self.count) * "\n")


class File(core.Object):
    instructions: list[Instruction] = core.Field(
        description="Dockerfile instruction list",
        default_factory=list,
    )

    def write(self, buffer: TextIO):
        for instruction in self.instructions:
            instruction.write(buffer)

    def __iadd__(self, instruction: Instruction):
        self.instructions.append(instruction)
        return self
