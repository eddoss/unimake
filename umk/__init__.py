# utils
from pathlib import Path

# project
from .project import Author
from .project import Name as ProjectName
from .project import Info as ProjectInfo
from .project import Description as ProjectDescription
from .project import register

# framework
from . import project as projects
from .project.base import get as project
from .globals import Global
from . import framework
