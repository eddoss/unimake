from umk import framework, core
from umk.dot.instance import Dot
from umk.framework.project.base import Project

Instance: Dot | None = Dot()
ErrorPrinter: core.ErrorPrinter = core.ErrorPrinter()


# ////////////////////////////////////////////////////////////////////////////////////
# Remote environments implementation
# ////////////////////////////////////////////////////////////////////////////////////

@core.typeguard
def find_remote(name: str = "") -> framework.remote.Interface | None:
    global Instance
    if not Instance:
        return
    if not name:
        for remote in Instance.remotes.values():
            if remote.default:
                return remote
    else:
        return Instance.remotes.get(name)


def iterate_remotes():
    global Instance
    for rem in Instance.remotes.values():
        yield rem


framework.remote.find = find_remote
framework.remote.iterate = iterate_remotes


# ////////////////////////////////////////////////////////////////////////////////////
# Project implementation
# ////////////////////////////////////////////////////////////////////////////////////

def get_project() -> Project | None:
    global Instance
    return Instance.project


framework.project.get = get_project


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
