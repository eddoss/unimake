from .container import Container
from .loader import OPT, YES, NO, Loader
from .loader import Options as LoadingOptions
from .errors import errors


container: None | Container = None


def load(options: LoadingOptions):
    global container
    container = Loader().load(options)
