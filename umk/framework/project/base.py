import string

from umk import core
from umk.framework import utils
from umk.framework.filesystem import Path


class BadProjectIdError(core.Error):
    def __init__(self, project_id: str, allowed: str, message: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [message]
        self.details.new(name="id", value=project_id, desc="Project ID value")
        self.details.new(name="allowed", value=allowed, desc="Allowed symbols")


class Contributor(core.Model):
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

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "Project.Info.Contributor"
        result.properties.new(name="Name", value=self.name, desc="Contributor name")
        result.properties.new(name="Email", value=self.email, desc="Contributor email")
        result.properties.new(name="Socials", value=self.socials, desc="Contributor social networks")
        return result


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
    contributors: list[Contributor] = core.Field(
        default_factory=list,
        description="Project contributors."
    )

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "Project.Info"
        result.properties.new(name="Id", value=self.id, desc="Project ID")
        result.properties.new(name="Name", value=self.name, desc="Project label")
        result.properties.new(name="Version", value=self.version, desc="Project version")
        result.properties.new(name="Description", value=self.description, desc="Project description")
        result.properties.new(name="Contributors", value=[c.object() for c in self.contributors], desc="Project contributors")
        return result

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

    @core.typeguard
    def contrib(self, name: str, email: str | list[str], socials: None | dict[str, str] = None):
        item = Contributor()
        item.name = name
        item.socials = socials or {}
        if issubclass(type(email), str):
            item.email.append(email)
        else:
            item.email = email
        self.contributors.append(item)


class Layout(core.Model):
    root: Path = core.Field(
        default=core.globals.paths.work,
        description="Project root directory."
    )
    unimake: Path = core.Field(
        default=core.globals.paths.work / ".unimake",
        description="'.unimake' root directory."
    )


class Interface:
    def __init__(self):
        self.info: Info = Info()
        self.layout: Layout = Layout()

    def release(self):
        """
        Release project.
        """
        self.__not_implemented()

    def __not_implemented(self):
        core.globals.console.print(
            f"[bold]The '{self.info.name or self.info.id}' has no '{utils.caller(2)}' action."
        )


class Scratch(Interface):
    pass


