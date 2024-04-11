import inspect

from umk.core.typings import Callable, Any
from umk import framework, core
from umk.runtime.container import utils


class ProjectSourceError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project entry outside of .unimake/project.py'"]


class ProjectAlreadyExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Project entry is already registered"]


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

    def __init__(self):
        self.object: framework.project.Project | None = None
        self.release: Callable[..., Any] | None = None
        self.defers = Project.Defers()
        self.loaded = False

    def call_release(self):
        if self.release is None:
            core.globals.console.print(f"[bold]Release action was not registered !")
        else:
            sig = len(inspect.signature(self.release).parameters)
            if sig == 0:
                self.release()
            elif sig == 1:
                self.release(framework.config.get())
            else:
                self.release(framework.config.get(), self.object)

    def releaser(self, func):
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

    def entry(self, factory):
        if self.loaded:
            return factory

        # Allow register just from .unimake/project.py
        frame = inspect.stack()[2]
        if not frame.filename.endswith(".unimake/project.py"):
            raise ProjectSourceError()

        # Register entry just one time
        if self.defers.entry:
            raise ProjectAlreadyExistsError()

        self.defers.entry = utils.Defer(func=factory)

        return factory

    def implement(self):
        framework.project.releaser = lambda f: self.releaser(f)
        framework.project.release = lambda f: self.release()
        framework.project.get = lambda: self.object
        framework.project.entry = lambda factory: self.entry(factory)

    def run_defers(self):
        if self.loaded:
            return
        if self.defers.entry:
            sig = len(inspect.signature(self.defers.entry.func).parameters)
            if sig == 0:
                self.object = self.defers.entry.func()
            else:
                self.object = self.defers.entry.func(framework.config.get())
            if not issubclass(type(self.object), framework.project.Project):
                raise ProjectBadTypeError()
        if self.defers.release:
            if not self.object:
                raise ProjectReleaseOrphanError()
            self.release = self.defers.release.func
        self.loaded = True
