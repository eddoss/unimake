from rich.console import Console
from pathlib import Path

console = Console()


class Config:
    class Paths:
        def __init__(self, root: Path):
            self.root = root
            self.work = self.root / '.unimake'
            self.dotenv = self.work / '.env'
            self.cli = self.work / 'cli.py'
            self.project = self.work / 'project.py'

    def __init__(self):
        self.paths = Config.Paths(Path.cwd())
        self.remote = ''
        self.pure = False


Global = Config()

