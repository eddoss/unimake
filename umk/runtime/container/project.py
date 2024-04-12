import inspect

from umk.core.typings import Callable, Any, Type
from umk import framework, core
from umk.runtime.container import utils


class ProjectNotRegisteredError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"No project registration was found. Put one in the .unimake/project.py'"]


class ProjectSourceError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project entry outside of .unimake/project.py'"]


class ProjectAlreadyExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Project is already registered"]


class ProjectBadTypeError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Project entry must be based on umk.framework.project.Project"]


class ProjectReleaseSourceError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project release function outside of .unimake/project.py'"]


class ProjectReleaseAlreadyExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Could not register project release: it is already exists"]


class ProjectReleaseNotFunctionError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project release function, only functions are allowed"]


class ProjectReleaseOrphanError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Could not register project release: project was not registered"]


class Project:
    class Defers:
        def __init__(self):
            self.entry: utils.Defer | None = None
            self.release: utils.Defer | None = None
            self.entry_type: Type = None

    def __init__(self):
        self.object: framework.project.Interface | None = None
        self.release: Callable[..., Any] | None = None
        self.defers = Project.Defers()
        self.loaded = False

    def call_release(self):
        if self.release is None:
            core.globals.console.print(f"[bold]Release action was not registered !")
        else:
            utils.call(self.release, 0, 2, framework.config.get(), self.object)

    def register_release(self, func):
        if self.loaded:
            return func

        # Allow register just from .unimake/config.py
        frame = inspect.stack()[2]
        if not frame.filename.endswith(".unimake/project.py"):
            raise ProjectReleaseSourceError()

        # Allow only functions
        if not inspect.isfunction(func):
            raise ProjectReleaseNotFunctionError()

        # Allow only time register
        if self.defers.release:
            raise ProjectReleaseAlreadyExistsError()

        self.defers.release.func = func

        return func

    def register_class(self, factory):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="project",
            stack=3,
            messages=["Failed to register project outside of the @script"],
        )
        utils.validate_only_class(
            factory=factory,
            messages=["Use 'project.custom' decorator only with class based on 'project.Interface'"]
        )
        if self.defers.entry:
            raise ProjectAlreadyExistsError()
        self.defers.entry = utils.Defer(func=factory)
        return factory

    def register_func(self, factory, deco: str, t: Type):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="project",
            stack=3,
            messages=["Failed to register project outside of the @script"],
        )
        utils.validate_only_function(
            factory=factory,
            messages=[f"Use 'project.{deco}' decorator only with functions"]
        )
        if self.defers.entry:
            raise ProjectAlreadyExistsError()
        self.defers.entry = utils.Defer(func=factory)
        self.defers.entry_type = t
        return factory

    def implement(self):
        framework.project.releaser = lambda f: self.register_release(f)
        framework.project.release = lambda: self.call_release()
        framework.project.get = lambda: self.object
        framework.project.empty = lambda factory: self.register_func(factory, "empty", framework.project.Scratch)
        framework.project.golang = lambda factory: self.register_func(factory, "golang", framework.project.Golang)
        framework.project.custom = lambda factory: self.register_class(factory)

    def run_defers(self):
        if self.loaded:
            return
        if not self.defers.entry:
            raise ProjectNotRegisteredError()
        if self.defers.entry_type is None:
            self.object = self.defers.entry(0, 1, framework.config.get())
            utils.validate_only_subclass(
                obj=self.object,
                base=framework.project.Interface,
                messages=["Use 'project.custom' decorator only with class based on 'project.Interface'"]
            )
        else:
            self.object = self.defers.entry_type()
            self.defers.entry(1, 2, self.object, framework.config.get())
        if not issubclass(type(self.object), framework.project.Interface):
            raise ProjectBadTypeError()
        if self.defers.release:
            if not self.object:
                raise ProjectReleaseOrphanError()
            self.release = self.defers.release.func
        self.loaded = True
