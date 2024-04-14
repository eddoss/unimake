from umk import core
from umk import framework
from umk.core.typings import Type, Callable, Any
from umk.framework import config, project
from umk.runtime.container import utils


class EntryDecorator(utils.Decorator):
    klass: Type | None = core.Field(
        default=None,
        description="Project type to pass to entry function (Scratch, Golang, ...)"
    )


class Project(core.Model):
    class Decorators(core.Model):
        release: utils.Decorator = core.Field(
            description="Decorator of the project release function",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                module="project",
                single=True,
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register releaser outside of the .unimake/project.py"),
                    subject=utils.FunctionError("Failed to register release. Use 'project.releaser' with functions")
                )
            ),
        )
        entry: EntryDecorator = core.Field(
            description="Decorator of the project empty, golang, custom, ... functions",
            default_factory=lambda: EntryDecorator(
                stack=2,
                module="project",
                single=True,
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register project outside of the .unimake/project.py"),
                    single=utils.ExistsError("Failed to register project. It's already exists"),
                )
            )
        )
    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Project decorators"
    )
    releaser: Callable[..., Any] | None = core.Field(
        default=None,
        description="Project release function"
    )
    instance: project.Interface = core.Field(
        default_factory=project.Interface,
        description="Project instance"
    )

    def release(self):
        if self.releaser is None:
            core.globals.console.print(f"[bold]Release action was not registered !")
        else:
            utils.call(self.releaser, 0, 2, framework.config.get(), self.object)

    def entry(self, factory, target: str = "custom", klass: Type | None = None):
        self.decorator.entry.target = target
        self.decorator.entry.klass = klass
        if target == "custom":
            self.decorator.entry.input.subject = "class"
            self.decorator.entry.input.sig.min = 0
            self.decorator.entry.errors.subject = utils.ClassError(
                f"Failed to register project. Use 'umk.framework.project.custom' with functions"
            )
            self.decorator.entry.errors.base = utils.SubclassError(
                "Failed to register project. Entry must be based on umk.framework.project.Interface"
            )
        else:
            self.decorator.entry.subject = "function"
            self.decorator.entry.sig.min = 1
            self.decorator.entry.errors.sig = utils.SignatureError(
                f"Failed to register project. Function '{self.decorator.entry.defers[0].func.__name__}' must accept instance"
            )
            self.decorator.entry.errors.subject = utils.FunctionError(
                f"Failed to register project. Use 'umk.framework.project.{self.target} with functions"
            )
        return self.decorator.entry.register(factory)

    def init(self):
        framework.project.get = lambda: self.object
        framework.project.release = lambda: self.release()
        framework.project.releaser = self.decorator.release.register
        framework.project.empty = lambda f: self.entry(f, "empty", framework.project.Scratch)
        framework.project.golang = lambda f: self.entry(f, "golang", framework.project.Golang)
        framework.project.custom = lambda f: self.entry(f)

    def setup(self, c: config.Config):
        if not self.decorator.entry.registered:
            raise utils.NotRegisteredError(
                "No project registration was found. Put one in the .unimake/project.py'"
            )
        if self.decorator.entry.klass is None:
            self.instance = self.decorator.entry.defers[0](0, 1, c)
        else:
            self.instance = self.decorator.entry.klass()
            self.decorator.entry.defers[0](1, 2, self.instance, c)
        if self.decorator.release.registered:
            if not self.instance:
                raise utils.NotRegisteredError(
                    "Failed to register project releaser. No project registration was found. Put one in the .unimake/project.py'"
                )
            self.releaser = self.decorator.release.defers[0].func
        self.decorator.entry.skip = True
        self.decorator.release.skip = True
