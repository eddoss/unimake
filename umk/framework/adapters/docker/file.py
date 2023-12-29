from beartype.typing import TextIO
from umk import core


class Instruction(core.Object):
    def write(self, buffer: TextIO):
        pass


class Add(Instruction):
    """
    Add local or remote files and directories.
    """
    def write(self, buffer: TextIO):
        pass


class Arg(Instruction):
    """
    Use build-time variables.
    """
    def write(self, buffer: TextIO):
        pass


class Cmd(Instruction):
    """ 
    Specify default commands.
    """
    def write(self, buffer: TextIO):
        pass


class Copy(Instruction):
    """ 
    Copy files and directories.
    """
    def write(self, buffer: TextIO):
        pass


class Entrypoint(Instruction):
    """
    Specify default executable.
    """
    def write(self, buffer: TextIO):
        pass


class Env(Instruction):
    """
    Set environment variables.
    """
    def write(self, buffer: TextIO):
        pass


class Expose(Instruction):
    """
    Describe which ports your application is listening on.
    """
    def write(self, buffer: TextIO):
        pass


class From(Instruction):
    """
    Create a new build stage from a base image.
    """
    def write(self, buffer: TextIO):
        pass


class Healthcheck(Instruction):
    """
    Check a container's health on startup.
    """
    def write(self, buffer: TextIO):
        pass


class Label(Instruction):
    """
    Add metadata to an image.
    """
    def write(self, buffer: TextIO):
        pass


class Maintainer(Instruction):
    """
    Specify the author of an image.
    """
    def write(self, buffer: TextIO):
        pass


class Onbuild(Instruction):
    """
    Specify instructions for when the image is used in a build.
    """
    def write(self, buffer: TextIO):
        pass


class Run(Instruction):
    """
    Execute build commands.
    """
    def write(self, buffer: TextIO):
        pass


class Shell(Instruction):
    """
    Set the default shell of an image.
    """
    def write(self, buffer: TextIO):
        pass


class Stopsignal(Instruction):
    """
    Specify the system call signal for exiting a container.
    """
    def write(self, buffer: TextIO):
        pass


class User(Instruction):
    """
    Set user and group ID.
    """
    def write(self, buffer: TextIO):
        pass


class Volume(Instruction):
    """
    Create volume mounts.
    """
    def write(self, buffer: TextIO):
        pass


class Workdir(Instruction):
    """
    Change working directory.
    """
    def write(self, buffer: TextIO):
        pass


class Comment(Instruction):
    """
    Comment lines.
    """
    lines: list[str] = core.Field(
        description="Comment lines",
        default_factory=list,
    )


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
