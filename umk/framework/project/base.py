import string

from umk.typing import Callable, Type
from umk import globals, core
from umk.framework.filesystem import Path


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
            raise core.Error(
                msg=f"Project ID should not starts with digit",
                attrs={"Starts with": value[0]}
            )
        if value[0] in signs:
            raise core.Error(
                msg=f"Project ID should not starts with sign",
                attrs={"Starts with": value[0]}
            )
        if set(value) > allowed:
            raise core.Error(
                msg=f"Project ID should contains only alphas and any signs",
                attrs={"Alphas": "".join(alphabet), "Signs": "".join(signs)}
            )

        return value


class Layout(core.Model):
    root: Path = core.Field(
        default=globals.paths.work,
        description="Project root directory."
    )
    unimake: Path = core.Field(
        default=globals.paths.work / ".unimake",
        description="'.unimake' root directory."
    )


class Project:
    def __init__(self):
        self.info: Info = Info()


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


class Scratch(Project):
    pass


class GolangLayout(Layout):
    root: Path = core.Field(
        default_factory=lambda: globals.paths.work,
        description="Layout root directory (golang project root)."
    )

    @property
    def assets(self): return self.root / "assets"

    @property
    def build(self): return self.root / "build"

    @property
    def cmd(self): return self.root / "cmd"

    @property
    def configs(self): return self.root / "configs"

    @property
    def deployment(self): return self.root / "deployment"

    @property
    def docs(self): return self.root / "docs"

    @property
    def examples(self): return self.root / "examples"

    @property
    def githooks(self): return self.root / "githooks"

    @property
    def init(self): return self.root / "init"

    @property
    def internal(self): return self.root / "internal"

    @property
    def pkg(self): return self.root / "pkg"

    @property
    def scripts(self): return self.root / "scripts"

    @property
    def test(self): return self.root / "test"

    @property
    def third_party(self): return self.root / "third_party"

    @property
    def tools(self): return self.root / "tools"

    @property
    def vendor(self): return self.root / "vendor"

    @property
    def web(self): return self.root / "web"

    @property
    def website(self): return self.root / "website"

    @property
    def output(self): return self.root / "output"


class Golang(Scratch):
    def __init__(self):
        super().__init__()
        self.layout: GolangLayout = GolangLayout()
