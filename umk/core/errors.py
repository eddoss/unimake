import sys
import traceback

from umk.core import globals
from umk.core.properties import Properties
from umk.core.typings import Any, Callable, Type
from umk.core.typings import typeguard, Model, Field
from pydantic import ValidationError
from rich.table import Table


class Error(Exception):
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @typeguard
    def name(self, value: str):
        self._name = value

    @property
    def messages(self) -> list[str]:
        return self._messages

    @messages.setter
    @typeguard
    def messages(self, value: list[str]):
        self._messages = value

    @property
    def details(self) -> Properties:
        return self._details

    @details.setter
    @typeguard
    def details(self, value: Properties):
        self._details = value

    @property
    def dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "messages": self.messages,
            "details": [detail.model_dump() for detail in self.details]
        }

    @typeguard
    def __init__(self, name: str, *messages: str):
        super().__init__()
        self._messages = list(messages)
        self._details = Properties()
        self._name = name

    def __str__(self):
        return " ".join(self.messages)

    @typeguard
    def print(self, printer: Callable[[...], Any]):
        self.print_messages(printer)
        self.print_details(printer)

    @typeguard
    def print_messages(self, printer: Callable[[...], Any]):
        for message in self.messages:
            if message:
                printer(f"[red bold]{message}")

    @typeguard
    def print_details(self, printer: Callable[[...], Any]):
        cs = "[bold red]"
        rs = "[bold red]"
        table = Table(show_header=True, show_edge=True, show_lines=False)
        table.add_column("Name", justify="left", style=cs, no_wrap=True)
        table.add_column("Default", justify="center", style=cs, no_wrap=True)
        table.add_column("Description", justify="left", style=cs, no_wrap=True)
        for detail in self.details:
            table.add_row(detail.name, detail.value, detail.description, style=rs)
        printer(table)


class InternalError(Error):
    def __init__(self, name: str, *messages: str, **details):
        super().__init__(name, *messages, **details)


class UnknownError(Error):
    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @errors.setter
    @typeguard
    def errors(self, value: list[Exception]):
        self._errors = value
        self._messages = [str(err) for err in self._errors]

    def __init__(self, *errors: Exception):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self._errors = []
        self.errors = list(errors)


# ////////////////////////////////////////////////////////////////////////////////////
# Printer
# ////////////////////////////////////////////////////////////////////////////////////

class Printer(Model):
    printers: dict[Type, Callable[[Exception], None]] = Field(
        default_factory=dict,
        description="Per type printers."
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
        globals.error_console.print(error.__class__.__name__)
        globals.error_console.print(str(error))
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
            globals.error_console.print(table)


def register(*types): ...


def print_error(err: Exception): ...
