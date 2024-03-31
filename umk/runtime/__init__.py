from pathlib import Path

from .instance import Instance
from .loader import OPT, YES, NO, Loader
from .errors import errors


container: None | Instance = None


def load(root: Path, *, project=YES, remotes=YES, config=OPT, cli=YES):
    global container
    container = Loader().load(
        root,
        project=project,
        remotes=remotes,
        config=config,
        cli=cli
    )
