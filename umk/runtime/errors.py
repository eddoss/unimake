import sys
import traceback

from beartype.roar import BeartypeCallHintParamViolation
from beartype.roar import BeartypeCallHintReturnViolation
from umk import core
from umk.core.typings import Type, Callable
from rich.table import Table


class Printers(core.Model):
    printers: dict[Type, Callable[[Exception], None]] = core.Field(
        default_factory=dict,
        description="Per error type printers."
    )

    def __call__(self, error: Exception):
        t = type(error)
        if issubclass(t, SystemExit):
            return
        if t in self.printers:
            self.printers[t](error)
            self.stack(error)
            return

        # process unregistered exception type
        core.globals.error_console.print(error.__class__.__name__)
        core.globals.error_console.print(str(error))
        self.stack(error)

    def stack(self, error: Exception):
        table = Table(show_header=True, show_edge=True, show_lines=False)
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
            core.globals.error_console.print(table)

    def register(self, *types):
        def inner(func):
            def wrapped(error):
                return func
            for t in types:
                self.printers[t] = func
            return wrapped
        return inner


errors = Printers()

core.errors.register = lambda *types: errors.register(*types)


@core.errors.register(core.Error)
def on_error(error: core.Error):
    error.print(core.globals.error_console.print)


@core.errors.register(core.ValidationError)
def on_validation_error(error: core.ValidationError):
    core.globals.error_console.print(f"[red]Validation errors for type [bold yellow]'{error.title}'")
    for err in error.errors():
        core.globals.error_console.print(f"[bold green]\[{err['loc'][0]}][/] {err['msg']}")
        core.globals.error_console.print(f"├ expect {err['type']}")
        core.globals.error_console.print(f"╰▸given  {err['input']}")


@core.errors.register(BeartypeCallHintParamViolation)
def on_typeguard_param_violation(error: BeartypeCallHintParamViolation):
    core.globals.error_console.print(str(error))
