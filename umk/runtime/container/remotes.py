import inspect

from umk import framework, core
from umk.runtime.container import utils


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


class RemoteSourceError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Could not register remote environment outside of .unimake/remotes.py"]


class Remotes:
    class Defers:
        def __init__(self):
            self.ssh: list[utils.Defer] = []
            self.container: list[utils.Defer] = []
            self.compose: list[utils.Defer] = []
            self.custom: list[utils.Defer] = []

    @property
    def default(self) -> None | framework.remote.Interface:
        return self._list.get(self._default)

    @default.setter
    def default(self, value: str):
        self._default = value

    def __init__(self):
        self.loaded = False
        self.defers = Remotes.Defers()
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

    def register_ssh(self, factory):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="remotes",
            stack=3,
            messages=["Failed to register 'ssh' remote outside of the @script"],
        )
        utils.validate_only_function(
            factory=factory,
            messages=["Use 'remote.ssh' decorator only with functions"]
        )
        self.defers.ssh.append(utils.Defer(func=factory))
        return factory

    def register_compose(self, factory):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="remotes",
            stack=3,
            messages=["Failed to register 'docker.compose' remote outside of the @script"],
        )
        utils.validate_only_function(
            factory=factory,
            messages=["Use 'remote.docker.compose' decorator only with functions"]
        )
        self.defers.compose.append(utils.Defer(func=factory))
        return factory

    def register_container(self, factory):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="remotes",
            stack=3,
            messages=["Failed to register 'docker.container' remote outside of the @script"],
        )
        utils.validate_only_function(
            factory=factory,
            messages=["Use 'remote.docker.container' decorator only with functions"]
        )
        self.defers.container.append(utils.Defer(func=factory))
        return factory

    def register_custom(self, factory):
        if self.loaded:
            return factory
        utils.validate_source_module(
            script="remotes",
            stack=3,
            messages=["Failed to register 'custom' remote outside of the @script"],
        )
        utils.validate_only_class(
            factory=factory,
            messages=["Use 'remote.custom' decorator only with class based on 'remote.Interface'"]
        )
        self.defers.custom.append(utils.Defer(func=factory))
        return factory

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
            return self._list[name]

    def implement(self):
        framework.remote.find = lambda name="": self.find(name)
        framework.remote.iterate = lambda: self.__iter__()
        framework.remote.ssh = lambda factory: self.register_ssh(factory)
        framework.remote.docker.compose = lambda factory: self.register_compose(factory)
        framework.remote.docker.container = lambda factory: self.register_container(factory)
        framework.remote.custom = lambda factory: self.register_custom(factory)

    def run_defers(self):
        for defer in self.defers.custom:
            imp: framework.remote.Interface = defer.func()
            utils.validate_only_subclass(
                obj=imp,
                base=framework.remote.Interface,
                messages=["Use 'remote.custom' decorator only with class based on 'remote.Interface'"]
            )
            if imp.name in self._list:
                utils.raise_already_exists(messages=[f"Remote environment '{imp.name}' is already exists"])

        for defer in self.defers.ssh:
            imp = framework.remote.SecureShell()
            defer(1, 3, imp, framework.config.get(), framework.project.get())
            # TODO Validate imp.name
            imp.name = imp.name or defer.func.__name__
            if imp.name in self._list:
                utils.raise_already_exists(messages=[f"Remote environment '{imp.name}' is already exists"])
            if imp.default:
                if self._default:
                    raise RemoteDefaultAlreadyExistsError(
                        current=self._default,
                        given=imp.name,
                        factory=defer.func,
                        frame=inspect.stack()[2],
                    )
                self._default = imp.name
            self._list[imp.name] = imp

        for defer in self.defers.compose:
            imp = framework.remote.DockerCompose()
            defer(1, 3, imp, framework.config.get(), framework.project.get())
            # TODO Validate imp.name
            imp.name = imp.name or defer.func.__name__
            if imp.name in self._list:
                utils.raise_already_exists(messages=[f"Remote environment '{imp.name}' is already exists"])
            if imp.default:
                if self._default:
                    raise RemoteDefaultAlreadyExistsError(
                        current=self._default,
                        given=imp.name,
                        factory=defer.func,
                        frame=inspect.stack()[2],
                    )
                self._default = imp.name
            self._list[imp.name] = imp

        for defer in self.defers.container:
            imp = framework.remote.DockerContainer()
            defer(1, 3, imp, framework.config.get(), framework.project.get())
            # TODO Validate imp.name
            imp.name = imp.name or defer.func.__name__
            if imp.name in self._list:
                utils.raise_already_exists(messages=[f"Remote environment '{imp.name}' is already exists"])
            if imp.default:
                if self._default:
                    raise RemoteDefaultAlreadyExistsError(
                        current=self._default,
                        given=imp.name,
                        factory=defer.func,
                        frame=inspect.stack()[2],
                    )
                self._default = imp.name
            self._list[imp.name] = imp
