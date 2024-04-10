import inspect

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


class ConfigPresetSignatureError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Config preset "]


class ProjectActionIsOrphanError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Could not register project action: project entry was not registered"]


class ProjectActionAlreadyExistsError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project action: name '{name}' is already exists"]
        self.details.new(name="name", value=name, desc="Project action name")


class ProjectActionSourceError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register project action '{name}' outside of .unimake/project.py'"]
        self.details.new(name="name", value=name, desc="Project action name")


class ProjectActionNotFunctionError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Use project action register for function with signature 'def () -> None' / 'def (proj: Project-Type) -> None' / 'def (proj: Project-Type, conf: User-Config-Type) -> None' /  'def (conf: User-Config-Type) -> None' only. See '{name}' action"]
        self.details.new(name="name", value=name, desc="Project action name")


class Project:
    class Defers:
        def __init__(self):
            self.entry: utils.Defer | None = None
            self.actions: list[utils.Defer] = []

    def __init__(self):
        self.object: framework.project.Project | None = None
        self.actions: dict[str, framework.project.Action] = {}
        self.defers = Project.Defers()
        self.loaded = False

    def run(self, name: str):
        action = self.actions.get(name)
        if not action:
            core.globals.console.print(f"[yellow boldProject action: action '{name}' not found")
            return
        sig = len(inspect.signature(action).parameters)
        if sig == 0:
            action()
        elif sig == 1:
            action(self.object)
        else:
            action(self.object, framework.config.get())

    def action(self, func=None, *, name: str = ""):
        def validate(f, n, s):
            # Allow register just from .unimake/config.py
            frame = inspect.stack()[s]
            if not frame.filename.endswith(".unimake/project.py"):
                raise ProjectActionSourceError(n)

            # Allow only functions
            if not inspect.isfunction(f):
                raise ProjectActionNotFunctionError(n)

        # Without 'name'
        if func is not None:
            if not self.loaded:
                validate(func, func.__name__, 3)
                self.defers.actions.append(utils.Defer(func, name=func.__name__))
            return func

        def decorator(fu):
            # With 'name'
            if not self.loaded:
                validate(func, name, 2)
                self.defers.actions.append(utils.Defer(fu, name=name))
            return fu

        return decorator

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
        @core.overload
        def act(func): ...

        @core.overload
        def act(*, name: str = ""): ...

        def act(func=None, *, name: str = ""): return self.action(func, name=name)

        framework.project.action = act
        framework.project.get = lambda: self.object
        framework.project.run = lambda name: self.run(name)
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

            def release():
                """
                Release project
                """
                self.object.release()
            self.actions["release"] = release
        if self.defers.actions:
            if not self.object:
                raise ProjectActionIsOrphanError()
            for action in self.defers.actions:
                name = action.args.get("name")
                if name in self.actions:
                    raise ProjectActionAlreadyExistsError(name)
                self.actions[name] = action.func
        self.loaded = True
