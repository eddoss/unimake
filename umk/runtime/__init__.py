from pathlib import Path

from .instance import Instance
from .loader import OPT, YES, NO, Loader
from .loader import Options as LoadingOptions
from .errors import errors


container: None | Instance = None


def load(options: LoadingOptions):
    global container
    container = Loader().load(options)
