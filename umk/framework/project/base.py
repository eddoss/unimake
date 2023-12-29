import string

from beartype.typing import Callable, Type

from umk import globals, core


class Description:
    @property
    def short(self) -> str:
        return self._short

    @short.setter
    @core.typeguard
    def short(self, value: str):
        self._short = value

    @property
    def full(self) -> str:
        return self._full

    @full.setter
    @core.typeguard
    def full(self, value: str):
        self._full = value

    @core.typeguard
    def __init__(self, short: str = "", full: str = ""):
        self._short = short
        self._full = full


class Name(Description):
    @property
    def ok(self) -> bool:
        signs = set('.-+_')
        digits = set(string.digits)
        alphabet = set(string.ascii_lowercase)
        allowed = set()
        allowed.update(digits, signs, alphabet)

        return self.short != "" \
            and self.short[0] not in digits \
            and self.short[0] not in signs \
            and set(self.short) <= allowed

    @core.typeguard
    def __init__(self, short: str = '', full: str = ''):
        super().__init__(short, full)


class Author:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @core.typeguard
    def name(self, value: str):
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    @core.typeguard
    def email(self, value: str):
        self._email = value

    @property
    def socials(self) -> dict[str, str]:
        return self._socials

    @socials.setter
    @core.typeguard
    def socials(self, value: dict[str, str]):
        self._socials = value

    @core.typeguard
    def __init__(self, name: str = '', email: str = '', socials: dict[str, str] = None):
        self._name = name
        self._email = email
        self._socials = {} if not socials else socials


class Info:
    @property
    def name(self) -> Name:
        return self._name

    @name.setter
    @core.typeguard
    def name(self, value: Name):
        self._name = value

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    @core.typeguard
    def version(self, value: str):
        self._version = value

    @property
    def description(self) -> Description:
        return self._description

    @description.setter
    @core.typeguard
    def description(self, value: Description):
        self._description = value

    @property
    def authors(self) -> list[Author]:
        return self._authors

    @authors.setter
    @core.typeguard
    def authors(self, value: list[Author]):
        self._authors = value

    def __init__(self):
        self._name = Name()
        self._version = ""
        self._description = Description()
        self._authors = []


class Layout:
    def __init__(self, root=globals.paths.work):
        self.root = root
        self.umk = self.root / ".unimake"


class Project:
    @property
    def info(self) -> Info:
        return self._info

    @info.setter
    @core.typeguard
    def info(self, value: Info):
        self._info = value

    def __init__(self):
        self._info = Info()


class Registerer:
    @property
    def instance(self) -> Project:
        return self._creator()

    def __init__(self, value: Type | Callable[[] | Project] | None = None):
        self._creator = value


def register(creator):
    return Registerer(creator)


def get() -> Project | None:
    # See implementation in dot/implementation.py
    raise NotImplemented()
