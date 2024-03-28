import inspect

from umk import framework, core
from umk.dot.instance import Dot
from umk.framework.project.base import Project

Instance: Dot | None = Dot()
ErrorPrinter: core.ErrorPrinter = core.ErrorPrinter()


# ////////////////////////////////////////////////////////////////////////////////////
# Remote environments implementation
# ////////////////////////////////////////////////////////////////////////////////////

class RemoteTypeError(core.Error):
    def __init__(self, factory_type: str, factory_name: str, position: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [
            "The decorator 'umk.remote.register' must be used with functions "
            "(or classes) that returns 'umk.remote.Interface' implementation."
        ]
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="type", value=factory_type, desc="Remote environment factory type")


class RemoteDefaultAlreadyExistsError(core.Error):
    def __init__(self, current: str, given: str, factory_type: str, factory_name: str, position: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [
            f"Default remote ({current}) is already exist, but '{given}' is marked as default"
        ]
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="type", value=factory_type, desc="Remote environment factory type")
        self.details.new(name="current", value=current, desc="The name of the given default remote")
        self.details.new(name="given", value=given, desc="The name of the current default remote")


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
    def __init__(self, name: str, factory_name: str, position: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Remote '{name}' is already exist"]
        self.details.new(name="at", value=position, desc="File position")
        self.details.new(name="factory", value=factory_name, desc="Remote environment factory name")
        self.details.new(name="name", value=name, desc="Remote environment name")


@core.typeguard
def remote_find(name: str = "") -> framework.remote.Interface:
    global Instance
    if not name:
        # default remote request
        if not Instance.container.default_remote:
            raise RemoteDefaultNotExistsError()
        return Instance.container.remotes[Instance.container.default_remote]
    else:
        return Instance.container.remotes[name]


def remote_iterate():
    global Instance
    for rem in Instance.container.remotes.values():
        yield rem


def remote_register(factory):
    impl: framework.remote.Interface = factory()
    if not issubclass(type(impl), framework.remote.Interface):
        frame = inspect.stack()[1]
        raise RemoteTypeError(
            factory_type="function" if inspect.isfunction(factory) else "class",
            factory_name=factory.__name__,
            position=f"{frame.filename}:{frame.lineno}"
        )
    if not impl.name:
        impl.name = factory.__name__

    global Instance

    if impl.name in Instance.container.remotes:
        frame = inspect.stack()[1]
        raise RemoteAlreadyExistsError(
            name=impl.name,
            factory_name=factory.__name__,
            position=f"{frame.filename}:{frame.lineno}"
        )

    if impl.default:
        if Instance.container.default_remote:
            frame = inspect.stack()[1]
            raise RemoteDefaultAlreadyExistsError(
                current=Instance.container.default_remote,
                given=impl.name,
                factory_type="function" if inspect.isfunction(factory) else "class",
                factory_name=factory.__name__,
                position=f"{frame.filename}:{frame.lineno}"
            )
        else:
            Instance.container.default_remote = impl.name

    Instance.container.remotes[impl.name] = impl

    return factory


framework.remote.find = remote_find
framework.remote.iterate = remote_iterate
framework.remote.register = remote_register


# ////////////////////////////////////////////////////////////////////////////////////
# Project implementation
# ////////////////////////////////////////////////////////////////////////////////////

def project_get() -> Project | None:
    global Instance
    return Instance.container.project


def project_entry(func):
    global Instance
    Instance.container.project = func()

    # TODO Validate func result type and value

    Instance.container.actions["clean"] = lambda: Instance.container.project.clean()
    Instance.container.actions["build"] = lambda: Instance.container.project.build()
    Instance.container.actions["lint"] = lambda: Instance.container.project.lint()
    Instance.container.actions["format"] = lambda: Instance.container.project.format()
    Instance.container.actions["test"] = lambda: Instance.container.project.test()
    Instance.container.actions["bundle"] = lambda: Instance.container.project.bundle()
    Instance.container.actions["generate"] = lambda: Instance.container.project.generate()
    Instance.container.actions["release"] = lambda: Instance.container.project.release()

    return func


@core.overload
def project_action(func):
    ...


@core.overload
def project_action(*, name: str = ""):
    ...


def project_action_straightforward(name: str, act: framework.project.Action):
    global Instance
    Instance.container.actions[name] = act


def project_action(func=None, *, name: str = ""):
    # Without 'name'
    if func is not None:
        global Instance
        Instance.container.actions[func.__name__] = func
        return func

    def decorator(fu):
        # With 'name'
        global Instance
        Instance.container.actions[name] = fu
        return fu

    return decorator


def project_run(name: str):
    action = Instance.container.actions.get(name)
    if not action:
        # TODO Create error for this situation
        raise ValueError()
    sig = len(inspect.signature(action).parameters)
    if sig == 0:
        action()
    else:
        pro = project_get()
        action(pro)


framework.project.entry = project_entry
framework.project.get = project_get
framework.project.action = project_action
framework.project.run = project_run
framework.project.base.action_straightforward = project_action_straightforward


# ////////////////////////////////////////////////////////////////////////////////////
# Error printer
# ////////////////////////////////////////////////////////////////////////////////////

def error_register(*types):
    def inner(func):
        def wrapped(error):
            return func

        global ErrorPrinter
        for t in types:
            ErrorPrinter.printers[t] = func
        return wrapped

    return inner


def print_error(err: Exception):
    ErrorPrinter(err)


core.error_register = error_register
core.print_error = print_error


@error_register(core.Error)
def on_error(error: core.Error):
    error.print(core.globals.error_console.print)


@error_register(core.ValidationError)
def on_validation_error(error: core.ValidationError):
    core.globals.error_console.print(f"[red]Validation errors for type [bold yellow]'{error.title}'")
    for err in error.errors():
        core.globals.error_console.print(f"[bold green]\[{err['loc'][0]}][/] {err['msg']}")
        core.globals.error_console.print(f"├ expect {err['type']}")
        core.globals.error_console.print(f"╰▸given  {err['input']}")
