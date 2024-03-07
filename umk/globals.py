import logging
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from beartype.typing import Any
from umk import core


class Paths:
    def __init__(self, root: Path):
        self.work = root.expanduser().resolve().absolute()
        self.unimake = self.work / '.unimake'


console = Console()
handler = RichHandler(
    rich_tracebacks=True,
    show_time=False,
    console=console,
    markup=False,
)
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[handler],
)
log = logging.getLogger("rich")
paths = Paths(Path.cwd())
completion = ''
events = core.Emitter()


def print(*objects: Any):
    console.print(*objects)


def close(err: None | Exception):
    code = 0
    if err:
        code = -1
        log.fatal(msg=str(err))
    exit(code)


class EventNames:
    # REMOTES
    REMOTE_BUILD = "remote.build"
    REMOTE_DESTROY = "remote.destroy"
    REMOTE_UP = "remote.up"
    REMOTE_DOWN = "remote.down"
    REMOTE_EXECUTE = "remote.execute"
    REMOTE_SHELL = "remote.shell"
    REMOTE_UPLOAD = "remote.upload"
    REMOTE_UPLOAD_ITEM = "remote.upload.item"
    REMOTE_DOWNLOAD = "remote.download"
    REMOTE_DOWNLOAD_ITEM = "remote.download.item"

    # SYSTEM
    SYSTEM_ENV_REQUIRE = "system.environments.require"

    # FILESYSTEM
    FILESYSTEM_COPY = "filesystem.copy"
    FILESYSTEM_MOVE = "filesystem.move"
