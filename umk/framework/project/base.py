import string

from umk import core
from umk.core.typings import Callable, Type
from umk.framework.filesystem import Path
from umk.framework.project.dependencies import Dependency


class BadProjectIdError(core.Error):
    def __init__(self, project_id: str, allowed: str, message: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [message]
        self.details.new(name="id", value=project_id, desc="Project ID value")
        self.details.new(name="allowed", value=allowed, desc="Allowed symbols")


class Author(core.Model):
    name: str = core.Field(
        default="",
        description="Author name."
    )
    email: list[str] = core.Field(
        default_factory=list,
        description="Author emails."
    )
    socials: dict[str, str] = core.Field(
        default_factory=dict,
        description="Author social networks.",
    )


class Info(core.Model):
    id: str = core.Field(
        default="",
        description="Project ID."
    )
    name: str = core.Field(
        default="",
        description="Project name."
    )
    version: str = core.Field(
        default="",
        description="Project version."
    )
    description: str = core.Field(
        default="",
        description="Project description."
    )
    authors: list[Author] = core.Field(
        default_factory=list,
        description="Project authors."
    )

    @core.field.validator("id")
    @classmethod
    def _validate(cls, value: str):
        signs = set('.-+_')
        digits = set(string.digits)
        alphabet = set(string.ascii_lowercase)
        allowed = set()
        allowed.update(digits, signs, alphabet)

        if value[0] in digits:
            raise BadProjectIdError(
                project_id=value,
                allowed=string.ascii_lowercase,
                message="Project ID should not starts with digit"
            )
        if value[0] in signs:
            raise BadProjectIdError(
                project_id=value,
                allowed=string.ascii_lowercase,
                message="Project ID should not starts with signs"
            )
        if set(value) > allowed:
            raise BadProjectIdError(
                project_id=value,
                allowed=string.ascii_lowercase + string.digits + "".join(signs),
                message="Project ID should contains just alphas and signs"
            )

        return value


class Layout(core.Model):
    root: Path = core.Field(
        default=core.globals.paths.work,
        description="Project root directory."
    )
    unimake: Path = core.Field(
        default=core.globals.paths.work / ".unimake",
        description="'.unimake' root directory."
    )


class Project:
    def __init__(self):
        self.info: Info = Info()
        self.dependencies: dict[str, list[Dependency]] = {}


class Scratch(Project):
    pass


class Registerer:
    @property
    def instance(self) -> Project:
        return self._creator()

    def __init__(self, value: Type | Callable[[], Project] | None = None):
        self._creator = value


def register(creator):
    return Registerer(creator)


def get() -> Project | None:
    # See implementation in dot/implementation.py
    raise NotImplemented()



