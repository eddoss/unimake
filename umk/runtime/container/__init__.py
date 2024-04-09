from .config import Config
from .project import Project
from .remotes import Remotes
from .targets import Targets


class Container:
    def __init__(self):
        self.project = Project()
        self.remotes = Remotes()
        self.targets = Targets()
        self.config = Config()

    def implement(self):
        self.remotes.implement()
        self.project.implement()
        self.targets.implement()
        self.config.implement()
