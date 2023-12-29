from textwrap import dedent
from rich.syntax import Syntax
from rich.table import Table
from umk import globals
from beartype import beartype


# ####################################################################################
# Loading errors
# ####################################################################################


# Base class
# ------------------------------------------------------------------------------------

class State:
    def __init__(self, code: int = -1, name: str = "", ok: bool = False):
        super().__init__()
        self.code: int = code
        self.name: str = name
        self.ok: bool = ok

    def print(self): ...


# Loading errors: ok and internal error
# ------------------------------------------------------------------------------------

class Ok(State):
    def __init__(self):
        super().__init__(code=0, name="Ok", ok=True)


class InternalError(State):
    @beartype
    def __init__(self, script: str, description: str):
        super().__init__(code=-1, name="Internal error")
        self._description = description
        self._script = script

    def print(self):
        desc = self._description if self._description else "No error description"
        globals.print(
            f"[red bold]Unimake internal error occurred when loaded '{self._script}'!\n"
            f"{desc}"
        )


# Loading errors: .unimake directory problems
# ------------------------------------------------------------------------------------

_table_init = Table(show_header=False, show_edge=True, show_lines=False)
_table_init.add_column("", justify="left", style="green bold", no_wrap=True)
_table_init.add_column("", justify="left", style="green", no_wrap=True)
_table_init.add_row('$ unimake init --help', 'Get initialization details')
_table_init.add_row('$ unimake init ...', 'Initialize a project')


class RootNotExists(State):
    @beartype
    def __init__(self):
        super().__init__(code=100, name="Root not exists")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "Current directory is not a Unimake project. "
            "Unimake project must contain '.unimake' directory with 'project.py' script. "
            "If you need to create a project get initialization help at first and after "
            "setup a '.unimake'"
        )
        globals.print(_table_init)


class RootNotDirectory(State):
    @beartype
    def __init__(self):
        super().__init__(code=101, name="Root it not a directory")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "Found [underline]'.unimake'[/underline] but it's not a folder. "
            "Try to remove '.unimake' at first and init a project."
        )
        globals.print(_table_init)


# Loading errors: .unimake/project.py problems
# ------------------------------------------------------------------------------------

class ProjectScriptNotExists(State):
    @beartype
    def __init__(self):
        super().__init__(code=200, name="No project.py")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "File [underline].unimake/project.py[/underline] does not exists"
        )


_project_register_function = dedent("""
import umk

@umk.register
def project(): 
    proj = umk.Project() # or umk.GoProject, etc
    proj.info.name.short = "super-project"
    proj.info.name.full = "Super mega project"
    proj.info.description.short = "Super project description"

    return proj
""")

_project_register_class = dedent("""
import umk

@umk.register
class Project(umk.GoProject):
    def __init__(self):
        super().__init__()
        self.info.name.short = "super-project"
        self.info.description.short = "Super project description"
""")


class ProjectCreatorNotExists(State):
    @beartype
    def __init__(self):
        super().__init__(code=201, name="No project creator")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "[underline].unimake/project.py[/underline] must register project\n"
        )
        globals.print("[bold red]Example with function:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )
        globals.print("[bold red]Example with class:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )


class ProjectCreatorBadType(State):
    @beartype
    def __init__(self):
        super().__init__(code=202, name="Project creator bad type")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "[underline].unimake/project.py[/underline] must register valid project type\n"
        )
        globals.print("[bold red]Example with function:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )
        globals.print("[bold red]Example with class:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )


# Loading errors: .unimake/remotes.py problems
# ------------------------------------------------------------------------------------

class RemotesScriptNotExists(State):
    @beartype
    def __init__(self):
        super().__init__(code=300, name="No remotes.py")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "File [underline].unimake/remotes.py[/underline] does not exists"
        )


_remote_register_function = dedent("""
from umk import remote

@remote.register
def ssh():
    env = umk.Environs()
    return remote.Ssh(
        name='ssh',
        description='Example remote environment',
        host=env.get('SSH_ADDR'),
        username=env.get('SSH_USER'),
        password=env.get('SSH_PASS'),
        shell='zsh'
    )
""")

_remote_register_class = dedent("""
import umk

@remote.register
class MySecreteRemote(remote.Ssh):
    def __init__(self):
        super().__init__()
        self.name="ssh",
        self.description="Example remote environment",
        self.host=env.get("SSH_ADDR"),
        self.username=env.get("SSH_USER"),
        self.password=env.get("SSH_PASS"),
        self.shell="zsh"
""")


class RemoteCreatorBadType(State):
    @beartype
    def __init__(self):
        super().__init__(code=301, name="Project creator bad type")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "[underline].unimake/remotes.py[/underline] must register valid remotes type\n"
        )
        globals.print("[bold red]Example with function:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )
        globals.print("[bold red]Example with class:\n")
        globals.print(
            Syntax(_project_register_function, "python", theme='monokai', line_numbers=False)
        )


# Loading errors: .unimake/cli.py problems
# ------------------------------------------------------------------------------------

class CliScriptNotExists(State):
    @beartype
    def __init__(self):
        super().__init__(code=400, name="No remotes.py")

    def print(self):
        globals.print(
            "[bold red]Unimake error !\n"
            "File [underline].unimake/remotes.py[/underline] does not exists"
        )
