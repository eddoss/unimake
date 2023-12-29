import copy
import dotenv
import sys
from umk import framework
from umk.framework.remote.registerer import Registerer as RemoteInterfaceRegisterer
from enum import Enum
from pathlib import Path
from importlib import util as importer
from umk import globals
from umk.framework.project.base import Project
from umk.framework.project.base import Registerer as ProjectRegisterer
from umk.dot import states


class Require(Enum):
    YES = 0     # required
    NO = 1      # not required
    OPT = 2     # required if exists


OPT = Require.OPT
YES = Require.YES
NO = Require.NO


class Containers:
    def __init__(self):
        self.project: Project | None = None
        self.remotes: dict[str, framework.remote.Interface] = {}


class Dot:
    @property
    def project(self) -> Project | None:
        return self._containers.project

    @property
    def remotes(self) -> dict[str, framework.remote.Interface]:
        return self._containers.remotes

    def __init__(self):
        self._root = Path()
        self._modules = {}
        self._containers = Containers()

    def load(
        self,
        root: Path, *,
        project: Require = Require.NO,
        remotes: Require = Require.NO,
        cli: Require = Require.NO
    ) -> states.State:
        self._root = root.expanduser().resolve().absolute()
        if not self._root.exists():
            return states.RootNotExists()
        if not self._root.is_dir():
            return states.RootNotDirectory()

        sys.path.insert(0, root.as_posix())

        try:
            file = self._root / '.env'
            dotenv.load_dotenv(file)
        finally:
            pass

        state = self._load_project(project)
        if not state.ok:
            return state
        state = self._load_remotes(remotes)
        if not state.ok:
            return state
        state = self._load_cli(cli)
        if not state.ok:
            return state

        return state

    def _load_cli(self, require: Require) -> states.State:
        if require == Require.NO:
            return states.Ok()
        try:
            self._script('cli')
        except FileNotFoundError:
            if require == Require.OPT:
                return states.Ok()
            return states.CliScriptNotExists()
        except Exception as e:
            return states.InternalError(script="cli.py", description=str(e))
        return states.Ok()

    def _load_project(self, require: Require) -> states.State:
        if require == Require.NO:
            return states.Ok()
        try:
            self._script('project')
        except FileNotFoundError:
            if require == Require.OPT:
                return states.Ok()
            return states.ProjectScriptNotExists()
        except Exception as e:
            return states.InternalError(script="project.py", description=str(e))

        module = self._modules.get('project')

        # Find project creator
        for _, value in module.__dict__.items():
            if issubclass(type(value), ProjectRegisterer):
                self._containers.project = copy.deepcopy(value.instance)
                break

        if self._containers.project is None:
            return states.ProjectCreatorNotExists()
        elif not issubclass(type(self._containers.project), Project):
            return states.ProjectCreatorBadType()

        return states.Ok()

    def _load_remotes(self, require: Require):
        if require == Require.NO:
            return states.Ok()
        try:
            self._script('remotes')
        except FileNotFoundError:
            if require == Require.OPT:
                return states.Ok()
            return states.RemotesScriptNotExists()
        except Exception as e:
            return states.InternalError(script="remotes.py", description=str(e))

        module = self._modules.get('remotes')

        # Find all and collect all remote interface registerer
        default: framework.remote.Interface | None = None
        for _, value in module.__dict__.items():
            if issubclass(type(value), RemoteInterfaceRegisterer):
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

        return states.Ok()

    def _script(self, name: str):
        if name in self._modules:
            globals.console.log(f"DotUnimake.script(): module '{name}' already exists")
            sys.exit(-1)
        file = self._root / f'{name}.py'
        if not file.exists():
            raise FileNotFoundError(f"fDotUnimake.script(): script does not exists: {file}")
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module
