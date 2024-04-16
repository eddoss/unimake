import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from umk.core.typings import Any


class Paths:
    def __init__(self, root: Path):
        self.work = root.expanduser().resolve().absolute()
        self.unimake = self.work / '.unimake'
        self.cache = self.unimake / ".cache"
        self.config = self.cache / "config.json"


console = Console()
error_console = Console(stderr=True, style="bold red")
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


def print(*objects: Any):
    console.print(*objects)


def close(code=0):
    exit(code)
