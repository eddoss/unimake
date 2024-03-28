import inspect

from umk import framework, core
from umk.framework.project import Project as BaseProject


class RemoteTypeError(core.Error):
    def __init__(self, factory, frame: inspect.FrameInfo):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [
            "The decorator 'umk.remote.register' must be used with functions "
            "(or classes) that returns 'umk.remote.Interface' implementation."
        ]
        factory_type = "function" if inspect.isfunction(factory) else "class"
        factory_name = factory.__name__
        position = f"{frame.filename}:{frame.lineno}"
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="type", value=factory_type, desc="Remote environment factory type")


class RemoteDefaultNotExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"No remote marked as default"]


class RemoteNotFoundError(core.Error):
    def __init__(self, name: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Remote environment '{name}' not found"]
        self.details.new(name="name", value=name, desc="Requested remote environment name")


class RemoteAlreadyExistsError(core.Error):
    def __init__(self, name: str, factory, frame: inspect.FrameInfo):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Remote '{name}' is already exist"]
        factory_name = factory.__name__
        position = f"{frame.filename}:{frame.lineno}"
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="name", value=name, desc="Remote environment name")


class RemoteDefaultAlreadyExistsError(core.Error):
    def __init__(self, current: str, given: str, factory, frame: inspect.FrameInfo):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [
            f"Default remote ({current}) is already exist, but '{given}' is marked as default"
        ]
        factory_type = "function" if inspect.isfunction(factory) else "class"
        factory_name = factory.__name__
        position = f"{frame.filename}:{frame.lineno}"
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="type", value=factory_type, desc="Remote environment factory type")
        self.details.new(name="current", value=current, desc="The name of the given default remote")
        self.details.new(name="given", value=given, desc="The name of the current default remote")


class Remotes:
    @property
    def default(self) -> None | framework.remote.Interface:
        return self._list.get(self._default)

    @default.setter
    def default(self, value: str):
        self._default = value

    def __init__(self):
        self._default: str = ""
        self._list: dict[str, framework.remote.Interface] = {}

    def __iter__(self):
        for rem in self._list.values():
            yield rem

    def __getitem__(self, name: str):
        return self._list[name]

    def __setitem__(self, name: str, impl: framework.remote.Interface):
        self._list[name] = impl

    def __len__(self):
        return len(self._list)

    def register(self, factory):
        impl: framework.remote.Interface = factory()
        if not issubclass(type(impl), framework.remote.Interface):
            raise RemoteTypeError(factory, inspect.stack()[1])
        if not impl.name:
            impl.name = factory.__name__

        if impl.name in self._list:
            raise RemoteAlreadyExistsError(name=impl.name, factory=factory, frame=inspect.stack()[1])

        if impl.default:
            if self._default:
                raise RemoteDefaultAlreadyExistsError(
                    current=self._default,
                    given=impl.name,
                    factory=factory,
                    frame=inspect.stack()[1],
                )
            self._default = impl.name
        self._list[impl.name] = impl

        return factory

    def find(self, name: str = "") -> None | framework.remote.Interface:
        if not name:
            # default remote request
            if not self._default:
                raise RemoteDefaultNotExistsError()
            return self._list[self._default]
        else:
            return self._list[self._default]

    def implement(self):
        framework.remote.find = lambda name="": self.find(name)
        framework.remote.iterate = lambda: self.__iter__()
        framework.remote.register = lambda factory: self.register(factory)


class Project:
    def __init__(self):
        self.object: BaseProject = None
        self.actions: dict[str, framework.project.Action] = {}

    def run(self, name: str):
        action = self.actions.get(name)
        if not action:
            # TODO Create error for this situation
            raise ValueError()
        sig = len(inspect.signature(action).parameters)
        if sig == 0:
            action()
        else:
            action(self.object)

    def action(self, func=None, *, name: str = ""):
        # Without 'name'
        if func is not None:
            self.actions[func.__name__] = func
            return func

        def decorator(fu):
            # With 'name'
            self.actions[name] = fu
            return fu

        return decorator

    def entry(self, factory):
        self.object = factory()

        # TODO Validate func result type and value

        self.actions["clean"] = lambda: self.object.clean()
        self.actions["build"] = lambda: self.object.build()
        self.actions["lint"] = lambda: self.object.lint()
        self.actions["format"] = lambda: self.object.format()
        self.actions["test"] = lambda: self.object.test()
        self.actions["bundle"] = lambda: self.object.bundle()
        self.actions["generate"] = lambda: self.object.generate()
        self.actions["documentation"] = lambda: self.object.documentation()
        self.actions["release"] = lambda: self.object.release()

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


class Instance:
    def __init__(self):
        self.project: Project = Project()
        self.remotes: Remotes = Remotes()

    def implement(self):
        self.remotes.implement()
        self.project.implement()

