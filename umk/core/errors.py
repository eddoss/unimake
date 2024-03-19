from umk.core.typing import Any, Callable
from umk.core.typing import typeguard
from umk.core.properties import Property
from umk.core.properties import Properties


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
    def print(self, printer: Callable[[...], Any]): ...


class PrintableError(Error):
    @property
    def elements(self) -> list[Any]:
        return self._elements

    @elements.setter
    @typeguard
    def elements(self, value: list[Any]):
        self._elements = value

    def __init__(self, name: str, *messages: str, **details):
        super().__init__(name, *messages, **details)
        self._elements = []

    @typeguard
    def print(self, printer: Callable[[...], Any]):
        for element in self.elements:
            printer(element)


class InternalError(PrintableError):
    def __init__(self, name: str, *messages: str, **details):
        super().__init__(name, *messages, **details)


class UnknownError(PrintableError):
    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @errors.setter
    @typeguard
    def errors(self, value: list[Exception]):
        self._errors = value
        self._elements = []
        self._messages = []
        for error in self._errors:
            self._elements += str(error)
            self._messages += str(error)

    def __init__(self, *errors: Exception):
        super().__init__(name=type(self).__name__)
        self._errors = list(errors)
