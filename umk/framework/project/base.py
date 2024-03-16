import string

from beartype.typing import Callable, Type
from umk import globals, core
from umk.framework.filesystem import Path


class Description(core.Model):
    short: str = ""
    full: str = ""


class Name(Description):
    @core.field.validator("short")
    @classmethod
    def _validate(cls, value: str):
        signs = set('.-+_')
        digits = set(string.digits)
        alphabet = set(string.ascii_lowercase)
        allowed = set()
        allowed.update(digits, signs, alphabet)

        if value[0] in digits:
            raise ValueError(f"Name should not starts with digit: {value}")
        if value[0] in signs:
            raise ValueError(f"Name should not starts with sign: {value}")
        if set(value) > allowed:
            raise ValueError(f"Name should contains only [alphas {' '.join(signs)}]: {value}")


class Author:
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


class Info:
    name: Name = core.Field(
        default_factory=Name,
        description="Project name."
    )
    version: str = core.Field(
        default="",
        description="Project version."
    )
    description: Description = core.Field(
        default_factory=Description,
        description="Project description."
    )
    authors: list[Author] = core.Field(
        default_factory=list,
        description="Project authors."
    )


class Layout:
    root: Path = core.Field(
        default=globals.paths.work,
        description="Project root directory."
    )
    unimake: Path = core.Field(
        default=globals.paths.work / ".unimake",
        description="'.unimake' root directory."
    )


class Project:
    info: Info = core.Field(
        default_factory=Info,
        description="Project info."
    )


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


class Scratch(Project):
    pass


class GoLayout(Layout):
    assets: Path = core.Field(
        default_factory=lambda: globals.paths.work / "assets",
        description="Path to 'assets' directory."
    )
    build: Path = core.Field(
        default_factory=lambda: globals.paths.work / "build",
        description="Path to 'build' directory."
    )
    cmd: Path = core.Field(
        default_factory=lambda: globals.paths.work / "cmd",
        description="Path to 'cmd' directory."
    )
    configs: Path = core.Field(
        default_factory=lambda: globals.paths.work / "configs",
        description="Path to 'configs' directory."
    )
    deployment: Path = core.Field(
        default_factory=lambda: globals.paths.work / "deployment",
        description="Path to 'deployment' directory."
    )
    docs: Path = core.Field(
        default_factory=lambda: globals.paths.work / "docs",
        description="Path to 'docs' directory."
    )
    examples: Path = core.Field(
        default_factory=lambda: globals.paths.work / "examples",
        description="Path to 'examples' directory."
    )
    githooks: Path = core.Field(
        default_factory=lambda: globals.paths.work / "githooks",
        description="Path to 'githooks' directory."
    )
    init: Path = core.Field(
        default_factory=lambda: globals.paths.work / "init",
        description="Path to 'init' directory."
    )
    internal: Path = core.Field(
        default_factory=lambda: globals.paths.work / "internal",
        description="Path to 'internal' directory."
    )
    pkg: Path = core.Field(
        default_factory=lambda: globals.paths.work / "pkg",
        description="Path to 'pkg' directory."
    )
    scripts: Path = core.Field(
        default_factory=lambda: globals.paths.work / "scripts",
        description="Path to 'scripts' directory."
    )
    test: Path = core.Field(
        default_factory=lambda: globals.paths.work / "test",
        description="Path to 'test' directory."
    )
    third_party: Path = core.Field(
        default_factory=lambda: globals.paths.work / "third_party",
        description="Path to 'third_party' directory."
    )
    tools: Path = core.Field(
        default_factory=lambda: globals.paths.work / "tools",
        description="Path to 'tools' directory."
    )
    vendor: Path = core.Field(
        default_factory=lambda: globals.paths.work / "vendor",
        description="Path to 'vendor' directory."
    )
    web: Path = core.Field(
        default_factory=lambda: globals.paths.work / "web",
        description="Path to 'web' directory."
    )
    website: Path = core.Field(
        default_factory=lambda: globals.paths.work / "website",
        description="Path to 'website' directory."
    )
    output: Path = core.Field(
        default_factory=lambda: globals.paths.work / "output",
        description="Path to 'output' directory."
    )


class GoProject(Scratch):
    layout: GoLayout = core.Field(
        default_factory=GoLayout,
        description="Golang project structure."
    )
