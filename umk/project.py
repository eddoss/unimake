import string

from beartype import beartype


class Name:
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

    @property
    def short(self) -> str:
        return self._short

    @short.setter
    @beartype
    def short(self, value: str):
        self._short = value

    @property
    def full(self) -> str:
        return self._full

    @full.setter
    @beartype
    def full(self, value: str):
        self._full = value

    def __init__(self):
        self._short = ""
        self._full = ""


class Author:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        self._name = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    @beartype
    def email(self, value: str):
        self._email = value

    @property
    def socials(self) -> dict[str, str]:
        return self._socials

    @socials.setter
    @beartype
    def socials(self, value: dict[str, str]):
        self._socials = value

    @beartype
    def __init__(self, name: str = '', email: str = '', socials: dict[str, str] = None):
        self._name = name
        self._email = email
        self._socials = {} if not socials else socials


class Info:
    @property
    def name(self) -> Name:
        return self._name

    @name.setter
    @beartype
    def name(self, value: Name):
        self._name = value

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    @beartype
    def version(self, value: str):
        self._version = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    @beartype
    def description(self, value: str):
        self._description = value

    @property
    def authors(self) -> list[Author]:
        return self._authors

    @authors.setter
    @beartype
    def authors(self, value: list[Author]):
        self._authors = value

    def __init__(self):
        self._name = Name()
        self._version = ""
        self._description = ""
        self._authors = []


class Project:
    @property
    def info(self) -> Info:
        return self._info

    @info.setter
    @beartype
    def info(self, value: Info):
        self._info = value

    def __init__(self):
        self._info = Info()
