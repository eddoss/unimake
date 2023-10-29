from rich.console import Console
from pathlib import Path


class Paths:
    def __init__(self, root: Path):
        self.work = root.expanduser().resolve().absolute()
        self.unimake = self.work / '.unimake'


class Globals:
    def __init__(self):
        self.paths = Paths(Path.cwd())
        self.console = Console()
        self.completion = False


Global = Globals()
