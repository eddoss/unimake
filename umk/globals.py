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
