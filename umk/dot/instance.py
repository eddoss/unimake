import copy
import sys
from enum import Enum
from importlib import util as importer
from pathlib import Path
from textwrap import dedent

import dotenv
from rich.syntax import Syntax
from rich.table import Table

from umk import framework, globals
from umk.core.errors import PrintableError, InternalError
from umk.dot import states
from umk.framework.project import Project as BaseProject
from umk.framework.project.base import Registerer as ProjectRegisterer
from umk.framework.remote.registerer import Registerer as RemoteRegisterer


class Require(Enum):
    YES = 0  # required
    NO = 1  # not required
    OPT = 2  # required if exists


OPT = Require.OPT
YES = Require.YES
NO = Require.NO


def _table_init():
    result = Table(show_header=False, show_edge=True, show_lines=False)
    result.add_column("", justify="left", style="green bold", no_wrap=True)
    result.add_column("", justify="left", style="green", no_wrap=True)
    result.add_row('$ unimake init --help', 'Get initialization details')
    result.add_row('$ unimake init ...', 'Initialize a project')
    return result


class RootNotExistsError(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load .unimake ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.elements += self.messages
        self.elements += [
            "[bold red]"
            "Current directory is not a Unimake project. "
            "Unimake project must contain '.unimake' directory with 'project.py' script. "
            "If you need to create a project get initialization help at first and after "
            "setup a '.unimake'",
            _table_init()
        ]


class RootIsNotDirectory(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load .unimake ! It is not a directory."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.elements += [
            "[bold red]"
            "Found [underline]'.unimake'[/underline] but it's not a folder. "
            "Try to remove '.unimake' at first and init a project.",
            _table_init()
        ]


class ProjectScriptNotExistsError(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load .unimake/project.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            "File [underline].unimake/project.py[/underline] does not exists"
        ]


class ProjectScriptLoadingError(PrintableError):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__)
        self.messages = [f"Failed to load .unimake/project.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            f"Failed to load [underline].unimake/project.py[/underline] ! {error}"
        ]


class ProjectNotRegisteredError(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load project instance ! It did not registered."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")
        by_function = dedent("""
        from umk.framework import project

        @umk.register
        def project(): 
            instance = project.Scratch() # or project.Golang, etc
            instance.info.id = "super-project"
            instance.info.name = "Super Project"
            instance.info.description = "Super mega project description"

            return instance
        """)
        by_class = dedent("""
        from umk.framework import project

        @project.register
        class Project(project.Golang):
            def __init__(self):
                super().__init__()
                self.info.id = "super-project"
                self.info.name = "Super Project"
                self.info.description = "Super mega project description"
        """)
        self.elements += [
            "[bold red]"
            "[underline].unimake/project.py[/underline] must register project\n"
            "Example with function:",
            Syntax(by_function, "python", theme='monokai', line_numbers=False),
            "Example with class:",
            Syntax(by_class, "python", theme='monokai', line_numbers=False),
        ]


class RemotesScriptNotExistsError(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load .unimake/remotes.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="remotes.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            "File [underline].unimake/remotes.py[/underline] does not exists"
        ]


class RemotesScriptLoadingError(PrintableError):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__)
        self.messages = [f"Failed to load .unimake/remotes.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="remotes.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            f"Failed to load [underline].unimake/remotes.py[/underline] ! {error}"
        ]


class CliScriptNotExistsError(PrintableError):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__)
        self.messages = ["Failed to load .unimake/cli.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="cli.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            "File [underline].unimake/cli.py[/underline] does not exists"
        ]


class CliScriptLoadingError(PrintableError):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__)
        self.messages = [f"Failed to load .unimake/cli.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="cli.py", desc="Script name.")
        self.elements += [
            "[red bold]"
            f"Failed to load [underline].unimake/cli.py[/underline] ! {error}"
        ]


class Containers:
    def __init__(self):
        self.project: BaseProject | None = None
        self.remotes: dict[str, framework.remote.Interface] = {}


class Dot:
    @property
    def project(self) -> BaseProject | None:
        return self._containers.project

    @property
    def remotes(self) -> dict[str, framework.remote.Interface]:
        return self._containers.remotes

    def __init__(self):
        self._root = Path()
        self._modules = {}
        self._containers = Containers()

    def load(self, root: Path, *, project=NO, remotes=NO, cli=NO):
        self._root = root.expanduser().resolve().absolute()
        if not self._root.exists():
            raise RootNotExistsError(self._root)
        if not self._root.is_dir():
            raise RootIsNotDirectory(self._root)

        sys.path.insert(0, root.as_posix())

        try:
            file = self._root / '.env'
            dotenv.load_dotenv(file)
        finally:
            pass

        self._load_project(project)
        self._load_remotes(remotes)
        self._load_cli(cli)

    def _load_project(self, require: Require):
        if require == NO:
            return
        try:
            self._script('project')
        except FileNotFoundError:
            if require == OPT:
                return
            raise ProjectScriptNotExistsError(self._root)
        except Exception as error:
            raise ProjectScriptLoadingError(self._root, error)

        module = self._modules.get('project')

        # Find project registered project creator
        for _, value in module.__dict__.items():
            if issubclass(type(value), ProjectRegisterer):
                self._containers.project = copy.deepcopy(value.instance)
                break

        if self._containers.project is None:
            raise ProjectNotRegisteredError(self._root)

    def _load_cli(self, require: Require):
        if require == NO:
            return
        try:
            self._script('cli')
        except FileNotFoundError:
            if require == OPT:
                return
            raise CliScriptNotExistsError(self._root)
        except Exception as error:
            raise CliScriptLoadingError(self._root, error)

    def _load_remotes(self, require: Require):
        if require == Require.NO:
            return states.Ok()
        try:
            self._script('remotes')
        except FileNotFoundError:
            if require == OPT:
                return
            raise RemotesScriptNotExistsError(self._root)
        except Exception as error:
            raise RemotesScriptLoadingError(self._root, error)

        module = self._modules.get('remotes')

        # Find all and collect all creators
        default: framework.remote.Interface | None = None
        for _, value in module.__dict__.items():
            if issubclass(type(value), RemoteRegisterer):
                impl: framework.remote.Interface = copy.deepcopy(value.instance)
                if impl.name not in self._containers.remotes:
                    if not default and impl.default:
                        default = impl
                    elif default and impl.default:
                        globals.console.print(
                            f"[bold yellow]WARNING! Default remote environment is already "
                            f"exists! Force '{impl.name}.default=False'[/]\n"
                            f"[bold underline]Given[/] \n"
                            f" - name '{impl.name}'\n"
                            f" - type '{impl.__class__.__module__}.{impl.__class__.__qualname__}'\n"
                            f" - desc '{impl.description}'\n"
                            f"[bold underline]Exist[/] \n"
                            f" - name '{default.name}'\n"
                            f" - type '{default.__class__.__module__}.{default.__class__.__qualname__}'\n"
                            f" - desc '{default.description}'\n"
                        )
                        impl.default = False
                    self._containers.remotes[impl.name] = impl
                else:
                    exist = self._containers.remotes.get(impl.name)
                    globals.print(
                        f"[bold yellow]WARNING! Skip '{impl.name}' remote environment, it is "
                        f"already exists![/]\n"
                        f"[bold underline]Given[/] \n"
                        f" - name '{impl.name}'\n"
                        f" - type '{impl.__class__.__module__}.{impl.__class__.__qualname__}'\n"
                        f" - desc '{impl.description}'\n"
                        f"[bold underline]Exist[/] \n"
                        f" - name '{exist.name}'\n"
                        f" - type '{exist.__class__.__module__}.{exist.__class__.__qualname__}'\n"
                        f" - desc '{exist.description}'\n"
                    )

    def _script(self, name: str):
        if name in self._modules:
            raise InternalError(
                "DotModuleExistsError",
                f"Module is already exists: {name}",
                name=name
            )
        file = self._root / f'{name}.py'
        if not file.exists():
            raise InternalError(
                "DotScriptLoadingError",
                f"Script does not exists: {file}",
                file=file
            )
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module
