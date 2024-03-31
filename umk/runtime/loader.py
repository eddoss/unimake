import sys
from enum import Enum
from importlib import util as importer
from pathlib import Path
from textwrap import dedent

import dotenv
from rich.syntax import Syntax
from rich.table import Table

from umk import framework, core
from umk.framework.project import Project as BaseProject
from umk.runtime.instance import Instance


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


class RootNotExistsError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")

    def print(self, printer):
        printer(
            "[bold red]"
            "Current directory is not a Unimake project. "
            "Unimake project must contain '.unimake' directory with 'project.py' script. "
            "If you need to create a project get initialization help at first and after "
            "setup a '.unimake'"
        )
        printer(_table_init())


class RootIsNotDirectory(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake ! It is not a directory."]
        self.details.new(name="root", value=root, desc="Path to .unimake")

    def print(self, printer):
        printer(
            "[bold red]"
            "Found [underline]'.unimake'[/underline] but it's not a folder. "
            "Try to remove '.unimake' at first and init a project."
        )
        printer(_table_init())


class ProjectScriptNotExistsError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake/project.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")


class ConfigScriptNotExistsError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake/config.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="config.py", desc="Script name.")


class ProjectScriptLoadingError(core.Error):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Failed to load .unimake/project.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")


class ProjectNotRegisteredError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load project instance ! It did not registered."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="project.py", desc="Script name.")

    def print(self, printer):
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
        self.print_messages(printer)
        printer("[bold red]Example with function:")
        printer(Syntax(by_function, "python", theme='monokai', line_numbers=False))
        printer("[bold red]Example with class:")
        printer(Syntax(by_class, "python", theme='monokai', line_numbers=False))


class RemotesScriptNotExistsError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake/remotes.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="remotes.py", desc="Script name.")


class RemotesScriptLoadingError(core.Error):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Failed to load .unimake/remotes.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="remotes.py", desc="Script name.")


class CliScriptNotExistsError(core.Error):
    def __init__(self, root: Path):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = ["Failed to load .unimake/cli.py ! It does not exists."]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="cli.py", desc="Script name.")


class CliScriptLoadingError(core.Error):
    def __init__(self, root: Path, error: Exception):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Failed to load .unimake/cli.py ! {error}"]
        self.details.new(name="root", value=root, desc="Path to .unimake")
        self.details.new(name="script", value="cli.py", desc="Script name.")


class DotInstanceAlreadyExistsError(core.Error):
    def __init__(self):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Failed to load '.unimake' ! It is already exists."]


class DotInstanceScriptLoadingError(core.Error):
    def __init__(self, path: Path, script: str, reason: str):
        super().__init__(name=type(self).__name__.rstrip("Error"))
        self.messages = [f"Failed to load '.unimake/{script}' ! {reason}"]
        self.details.new(name="script", value=script, desc="Script name.")
        self.details.new(name="path", value=path, desc=".unimake directory")
        self.details.new(name="reason", value=reason, desc="Reason.")


class Loader:
    def __init__(self):
        self._root = Path()
        self._modules = {}

    def load(self, root: Path, *, project=NO, remotes=NO, config=NO, cli=NO) -> Instance:
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

        result = Instance()
        result.implement()

        self.config(config)

        self.project(project)
        if project == YES and result.project.object is None:
            raise ProjectNotRegisteredError(self._root)

        self.remotes(remotes)

        return result

    def project(self, require: Require):
        if require == NO:
            return
        try:
            self._script('project')
        except FileNotFoundError:
            if require == OPT:
                return
            raise ProjectScriptNotExistsError(self._root)

    def remotes(self, require: Require):
        if require == Require.NO:
            return
        try:
            self._script('remotes')
        except FileNotFoundError:
            if require == OPT:
                return
            raise RemotesScriptNotExistsError(self._root)
        except Exception as error:
            raise RemotesScriptLoadingError(self._root, error)

    def config(self, require: Require):
        if require == NO:
            return
        try:
            self._script('config')
        except FileNotFoundError:
            if require == OPT:
                return
            raise ConfigScriptNotExistsError(self._root)

    def cli(self, require: Require):
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

    def _script(self, name: str):
        if name in self._modules:
            raise DotInstanceAlreadyExistsError()
        file = self._root / f'{name}.py'
        if not file.exists():
            raise DotInstanceScriptLoadingError(
                script=name,
                path=self._root,
                reason="Script file does not exists."
            )
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module

