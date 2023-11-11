import logging
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler


class Paths:
    def __init__(self, root: Path):
        self.work = root.expanduser().resolve().absolute()
        self.unimake = self.work / '.unimake'


class Globals:
    def __init__(self):
        self.console = Console()
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            console=self.console,
            markup=False,
        )
        logging.basicConfig(
            level="INFO",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[handler],
        )
        self.log = logging.getLogger("rich")
        self.paths = Paths(Path.cwd())
        self.completion = ''


Global = Globals()
