import logging
import traceback
from pathlib import Path

import rich.table
from rich.console import Console
from rich.logging import RichHandler
from umk.typing import Any, Type, Callable
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


def close(err: None | Exception):
    code = 0
    if err:
        code = -1
        log.fatal(msg=str(err))
    exit(code)


class EventNames:
    # REMOTES
    REMOTE_BUILD = "remote.build"
    REMOTE_DESTROY = "remote.destroy"
    REMOTE_UP = "remote.up"
    REMOTE_DOWN = "remote.down"
    REMOTE_EXECUTE = "remote.execute"
    REMOTE_SHELL = "remote.shell"
    REMOTE_UPLOAD = "remote.upload"
    REMOTE_UPLOAD_ITEM = "remote.upload.item"
    REMOTE_DOWNLOAD = "remote.download"
    REMOTE_DOWNLOAD_ITEM = "remote.download.item"

    # SYSTEM
    SYSTEM_ENV_REQUIRE = "system.environments.require"

    # FILESYSTEM
    FILESYSTEM_COPY = "filesystem.copy"
    FILESYSTEM_MOVE = "filesystem.move"


# ////////////////////////////////////////////////////////////////////////////////////
# Error printer
# ////////////////////////////////////////////////////////////////////////////////////

class ErrorPrinter(core.Model):
    printers: dict[Type, Callable[[Exception], None]] = core.Field(
        default_factory=dict,
        description="Per type printers."
    )

    def register(self, *types):
        def inner(func):
            def wrapped(error):
                return func
            for t in types:
                self.printers[t] = func
            return wrapped
        return inner

    def __call__(self, error: Exception):
        t = type(error)
        if issubclass(t, SystemExit):
            return
        if t in self.printers:
            self.printers[t](error)
            self.stack(error)
            return

        # process unregistered exception type
        print(error)
        self.stack(error)

    def stack(self, error: Exception):
        table = rich.table.Table(show_header=True, show_edge=True, show_lines=False)
        table.add_column("CALL STACK", justify="left", no_wrap=True)
        stack = traceback.TracebackException.from_exception(error).stack
        for frame in stack:
            if 'umk/dot' in frame.filename or \
                    'umk/framework' in frame.filename or \
                    'umk/kit' in frame.filename or \
                    'umk/tools' in frame.filename:
                link = f"{frame.filename}:{frame.lineno}"
                table.add_row(f"[link={link}]{link}[/link]")
        if len(table.rows):
            print(table)


error_printer = ErrorPrinter()


@error_printer.register(core.Error)
def error_printer_core(error: core.Error):
    print(f"[bold red]{error.message}")
    for name, value in error:
        print(f"[bold red] - {name} {value}")


@error_printer.register(core.TypeValidationError)
def error_printer_validation(error: core.TypeValidationError):
    print(f"[red]Validation errors for type [bold yellow]'{error.title}'")
    for err in error.errors():
        print(f"[bold green]\[{err['loc'][0]}][/] {err['msg']}")
        print(f"├ expect {err['type']}")
        print(f"╰▸given  {err['input']}")
