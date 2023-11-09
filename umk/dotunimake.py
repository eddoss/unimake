import dotenv
import sys
from enum import Enum
from pathlib import Path
from importlib import util as importer
from rich.syntax import Syntax
from rich.table import Table

from umk.globals import Global
from umk.project import Project
from beartype.typing import Optional


class LoadingState(Enum):
    OK = 0
    ROOT_NOT_EXISTS = 1
    ROOT_IS_NOT_DIR = 2
    PROJECT_PY_NOT_EXISTS = 3
    PROJECT_INSTANCE_NOT_EXISTS = 4
    REMOTE_PY_NOT_EXISTS = 5
    CLI_PY_NOT_EXISTS = 6
    DOT_ENV_NOT_EXISTS = 7


class Require(Enum):
    YES = 0     # required
    NO = 1      # not required
    OPT = 2     # required if exists


class DotUnimake:
    @property
    def project(self) -> Optional[Project]:
        return self._project_instance

    def __init__(self):
        self._root = Path()
        self._modules = {}
        self._project_instance: Optional[Project] = None

    def __getitem__(self, module_name: str):
        return self._modules[module_name]

    def load(
        self,
        root: Path, *,
        env: Require = Require.NO,
        project: Require = Require.NO,
        remotes: Require = Require.NO,
        cli: Require = Require.NO
    ) -> LoadingState:
        self._root = root.expanduser().resolve().absolute()
        if not self._root.exists():
            return LoadingState.ROOT_NOT_EXISTS
        if not self._root.is_dir():
            return LoadingState.ROOT_IS_NOT_DIR

        sys.path.insert(0, root.as_posix())

        state = self._load_dotenv(env)
        if state != LoadingState.OK:
            return state
        state = self._load_project(project)
        if state != LoadingState.OK:
            return state
        state = self._load_remotes(remotes)
        if state != LoadingState.OK:
            return state
        state = self._load_cli(cli)
        if state != LoadingState.OK:
            return state

        return LoadingState.OK

    def _load_dotenv(self, require: Require) -> LoadingState:
        if require == Require.NO:
            return LoadingState.OK
        file = self._root / '.env'
        if not file.exists():
            if require == Require.YES:
                return LoadingState.DOT_ENV_NOT_EXISTS
            else:
                return LoadingState.OK
        dotenv.load_dotenv(file)
        return LoadingState.OK

    def _load_cli(self, require: Require) -> LoadingState:
        if require == Require.NO:
            return LoadingState.OK
        if require == Require.YES:
            self._script('cli')
            return LoadingState.OK
        try:
            self._script('cli')
        finally:
            return LoadingState.OK

    def _load_project(self, require: Require) -> LoadingState:
        if require == Require.NO:
            return LoadingState.OK
        if require == Require.YES:
            self._script('project')
            module = self._modules.get('project')
            if not hasattr(module, 'project') or not issubclass(type(module.project), Project):
                return LoadingState.PROJECT_INSTANCE_NOT_EXISTS
            self._project_instance = module.project
            return LoadingState.OK
        try:
            self._script('project')
            self._project_instance = self._modules['project'].project
        finally:
            return LoadingState.OK

    def _load_remotes(self, require: Require):
        if require == Require.NO:
            return LoadingState.OK
        if require == Require.YES:
            self._script('remotes')
            return LoadingState.OK
        try:
            self._script('remotes')
        finally:
            return LoadingState.OK

    def _script(self, name: str):
        if name in self._modules:
            Global.console.log(f"DotUnimake.script(): module '{name}' already exists")
            sys.exit(-1)
        file = self._root / f'{name}.py'
        if not file.exists():
            raise FileNotFoundError(f"fDotUnimake.script(): script does not exists: {file}")
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module


class LoadingStateMessages:
    def __init__(self):
        self._table_init = Table(show_header=False, show_edge=True, show_lines=False)
        self._table_init.add_column("", justify="left", style="green bold", no_wrap=True)
        self._table_init.add_column("", justify="left", style="green", no_wrap=True)
        self._table_init.add_row('$ unimake init --help', 'Get initialization details')
        self._table_init.add_row('$ unimake init ...', 'Initialize a project')

    def on(self, state: LoadingState):
        match state:
            case LoadingState.ROOT_NOT_EXISTS:
                Global.console.print(
                    "[bold red]Unimake error !\n"
                    "Current directory is not a Unimake project. "
                    "Unimake project must contain '.unimake' directory with 'project.py' script. "
                    "If you need to create a project get initialization help at first and after "
                    "setup a '.unimake'"
                )
                Global.console.print(self._table_init)
            case LoadingState.ROOT_IS_NOT_DIR:
                Global.console.print(
                    "[bold red]Unimake error !\n"
                    "Found '.unimake' but it's not a folder. "
                    "Try to remove '.unimake' at first and init a project."
                )
                Global.console.print(self._table_init)
            case LoadingState.PROJECT_PY_NOT_EXISTS:
                Global.console.print(
                    "[bold red]Unimake error !\n"
                    "File [underline]'.unimake/project.py'[/underline] does not exists"
                )
            case LoadingState.PROJECT_INSTANCE_NOT_EXISTS:
                example = """
                import umk

                project = umk.Project() # or umk.GoProject, umk.CMakeProject, etc
                project.info.name.short = 'super-project'
                project.info.name.full = 'Super mega project'
                project.info.description = 'Super project description'
                """
                Global.console.print(
                    "[bold red]Unimake error !\n"
                    "Instance of the 'umk.Project' was not found !\n"
                    "File [underline]'.unimake/project.py'[/underline] must contains instance "
                    "of the Project"
                )
                Global.console.print(Syntax(example, "python", theme='monokai', line_numbers=False))
            case LoadingState.CLI_PY_NOT_EXISTS:
                Global.console.print(
                    "[bold red]Unimake error !\n"
                    "File [underline]'.unimake/cli.py'[/underline] does not exists"
                )
            case LoadingState.REMOTE_PY_NOT_EXISTS:
                Global.console(
                    f"[bold red]Unimake error !\n"
                    f"Failed to load .unimake/remote.py: does not exists"
                )


Unimake: Optional[DotUnimake] = DotUnimake()
