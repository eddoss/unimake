import io
import os
from datetime import timedelta

from umk import core
from umk.core.typings import TextIO, Optional, Any
from umk.framework.system.user import User as OSUser
from umk.framework.filesystem import Path


class Instruction(core.Model):
    def write(self, buffer: TextIO):
        pass

    def __str__(self):
        buf = io.StringIO()
        self.write(buf)
        return buf.getvalue()


class Commentable(Instruction):
    comment: list[str] = core.Field(
        description="Instruction comment lines",
        default_factory=list,
    )
    space: int = core.Field(
        description="Instruction pre-space count",
        default=0,
        exclude=True
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

    def write(self, buffer: TextIO):
        super().write(buffer)
        text = "ENTRYPOINT ["
        for i, arg in enumerate(self.args):
            text += f'"{arg}"' + [", ", ""][int(i == len(self.args) - 1)]
        text += "]\n"
        buffer.write(text)


class Env(Commentable):
    """
    Set environment variables.
    """
    name: str
    value: Any = None

    def write(self, buffer: TextIO):
        super().write(buffer)
        if self.value:
            text = f"ENV {self.name}={self.value}\n"
        else:
            text = f"ENV {self.name}\n"
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
    instruction: Instruction = core.Field(kw_only=False)

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
    separate: bool = core.Field(default=False)

    def write(self, buffer: TextIO):
        super().write(buffer)
        if self.separate:
            text = "\n".join([f"RUN {cmd}" for cmd in self.commands])
        else:
            text = "RUN " + " && \\\n    ".join(self.commands) + "\n"
        buffer.write(text)


class Shell(Commentable):
    """
    Set the default shell of an image.
    """
    args: list[str] = core.Field(default_factory=list)

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


class File(core.Model):
    instructions: core.typings.Adapter[list[Instruction]] = core.Field(
        default_factory=list,
        description="Dockerfile instruction list",
    )
    path: Path = core.Field(
        default_factory=Path,
        description="Dockerfile output directory",
    )
    name: str = core.Field(
        default="Dockerfile",
        description="Dockerfile output name",
    )

    def __repr__(self):
        return f"dockerfile://{str(self.file)}"

    def __str__(self):
        return self.text()

    @property
    def file(self) -> Path:
        if self.path is None:
            raise ValueError("Dockerfile: output path is None")
        return self.path / self.name

    def write(self, buffer: TextIO):
        for instruction in self.instructions:
            instruction.write(buffer)

    def save(self):
        file = self.file
        if not file.parent.exists():
            os.makedirs(file.parent)
        with open(file, "w") as stream:
            self.write(stream)

    def text(self) -> str:
        buf = io.StringIO()
        self.write(buf)
        return buf.getvalue()

    @core.typeguard
    def add(self, src: str, dst: str, chown: None | OSUser = None, chmod: None | int = None,
            checksum: None | str = None, *, space: int = 1, comment: list[str] = None):
        instruction = Add(comment=comment or [], space=space, src=src, dst=dst, chmod=chmod, chown=chown,
                          checksum=checksum)
        self.instructions.append(instruction)

    @core.typeguard
    def arg(self, name: str, value: Any = None, *, space: int = 1, comment: list[str] = None):
        instruction = Arg(comment=comment or [], space=space, name=name, value=value)
        self.instructions.append(instruction)

    @core.typeguard
    def cmd(self, args: list[str], *, space: int = 1, comment: list[str] = None):
        instruction = Cmd(comment=comment or [], space=space, args=args)
        self.instructions.append(instruction)

    @core.typeguard
    def copy(self, src: str, dst: str, chown: None | OSUser = None, chmod: None | int = None, *, space: int = 1,
             comment: list[str] = None):
        instruction = Copy(comment=comment or [], space=space, src=src, dst=dst, chmod=chmod, chown=chown)
        self.instructions.append(instruction)

    @core.typeguard
    def entrypoint(self, args: list[str], *, space: int = 1, comment: list[str] = None):
        instruction = Entrypoint(comment=comment or [], space=space, args=args)
        self.instructions.append(instruction)

    @core.typeguard
    def env(self, name: str, value: Any = None, *, space: int = 1, comment: list[str] = None):
        instruction = Env(comment=comment or [], space=space, name=name, value=value)
        self.instructions.append(instruction)

    @core.typeguard
    def expose(self, port: int, protocol: None | str = None, *, space: int = 1, comment: list[str] = None):
        instruction = Expose(comment=comment or [], space=space, port=port, protocol=protocol)
        self.instructions.append(instruction)

    @core.typeguard
    def froms(self, image: str, platform: None | str = None, alias: None | str = None, *, space: int = 0, comment: list[str] = None):
        instruction = From(comment=comment or [], space=space, image=image, platform=platform, alias=alias)
        self.instructions.append(instruction)

    @core.typeguard
    def healthcheck(
            self,
            interval: None | timedelta = None,
            timeout: None | timedelta = None,
            start_period: None | timedelta = None,
            start_interval: None | timedelta = None,
            retries: None | int = None,
            command: list[str] = None,
            *,
            space: int = 1,
            comment: list[str] = None
    ):
        instruction = Healthcheck(
            comment=comment or [],
            space=space,
            interval=interval,
            timeout=timeout,
            start_period=start_period,
            start_interval=start_interval,
            retries=retries,
            command=command
        )
        self.instructions.append(instruction)

    @core.typeguard
    def label(self, items: dict[str, str], *, space: int = 1, comment: list[str] = None):
        instruction = Label(comment=comment or [], space=space, items=items)
        self.instructions.append(instruction)

    @core.typeguard
    def maintainer(self, name: str, *, space: int = 1, comment: list[str] = None):
        instruction = Maintainer(comment=comment or [], space=space, name=name)
        self.instructions.append(instruction)

    @core.typeguard
    def on_build(self, instruction: Instruction, *, space: int = 1, comment: list[str] = None):
        inst = OnBuild(comment=comment or [], space=space, instruction=instruction)
        self.instructions.append(inst)

    @core.typeguard
    def run(self, commands: list[str], separate: bool = False, *, space: int = 1, comment: list[str] = None):
        instruction = Run(comment=comment or [], separate=separate, space=space, commands=commands)
        self.instructions.append(instruction)

    @core.typeguard
    def shell(self, args: list[str], *, space: int = 1, comment: list[str] = None):
        instruction = Shell(comment=comment or [], space=space, args=args)
        self.instructions.append(instruction)

    @core.typeguard
    def stop_signal(self, signal: int, *, space: int = 1, comment: list[str] = None):
        instruction = StopSignal(comment=comment or [], space=space, signal=signal)
        self.instructions.append(instruction)

    @core.typeguard
    def user(self, user: str | int, group: None | str | int = None, *, space: int = 1, comment: list[str] = None):
        instruction = User(comment=comment or [], space=space, user=str(user), group=str(group) if group else None)
        self.instructions.append(instruction)

    @core.typeguard
    def volume(self, path: str, *, space: int = 1, comment: list[str] = None):
        instruction = Volume(comment=comment or [], space=space, path=path)
        self.instructions.append(instruction)

    @core.typeguard
    def workdir(self, path: str, *, space: int = 1, comment: list[str] = None):
        instruction = Workdir(comment=comment or [], space=space, path=path)
        self.instructions.append(instruction)

    @core.typeguard
    def comment(self, *lines: str):
        instruction = Comment(lines=list(lines))
        self.instructions.append(instruction)

    @core.typeguard
    def space(self, count: int = 1):
        instruction = Space(count=count)
        self.instructions.append(instruction)

    def __iadd__(self, instruction: Instruction):
        self.instructions.append(instruction)
        return self

    def __str__(self) -> str:
        return self.text()

    @core.field.serializer("instructions")
    def _serialize_instructions(self, v: list[Instruction]):
        return [str(i).strip() for i in v]
