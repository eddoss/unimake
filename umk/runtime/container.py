import sys
from importlib import util as importer
from pathlib import Path

from umk import framework, core
from umk.runtime.config import Config
from umk.runtime.project import Project
from umk.runtime.targets import Targets
from umk.runtime.remotes import Remote


class Options(core.Model):
    class Config(core.Model):
        overrides: dict[str, framework.config.Value] = core.Field(
            default_factory=dict,
            description="Config entry overrides (passed by unimake CLI)"
        )
        presets: list[str] = core.Field(
            default_factory=list,
            description="Config presets to apply (passed by unimake CLI)"
        )
        file: bool = core.Field(
            default=False,
            description="Load config from file and modify it by preset and overrides"
        )

    root: Path = core.Field(
        default=core.globals.paths.unimake,
        description="Path to '.unimake' directory"
    )
    config: Config = core.Field(
        default_factory=Config,
        description="Config options"
    )


class Container:
    def __init__(self):
        self._modules = {}
        self.config = Config()
        self.project = Project()
        self.targets = Targets()
        self.remotes = Remote()

    def load(self, options: Options):
        root = options.root.expanduser().resolve().absolute()
        sys.path.insert(0, root.as_posix())

        with_config = (root / "config.py").exists()

        self.config.init()
        self.project.init()
        self.targets.init()
        self.remotes.init()

        if with_config:
            self.script(root, "config")
        self.script(root, "project")
        self.script(root, "remotes")

        if with_config:
            self.config.setup(options.config)
        self.project.setup(self.config.instance)
        self.targets.setup(self.config.instance, self.project.instance)
        self.remotes.setup(self.config.instance, self.project.instance)

    def find_remote(self, default: bool, specific: str) -> framework.remote.Interface:
        if default:
            result = self.remotes.get(self.remotes.default)
            if not result:
                core.globals.error_console.print(
                    'Failed to find default remote environment! '
                    'Please specify it in the .unimake/remotes.py'
                )
                core.globals.close(-1)
            return result
        if specific:
            result = self.remotes.get(specific)
            if not result:
                core.globals.console.print(
                    f"Failed to find remote environment '{specific}'! "
                    f"Please create it in the .unimake/remotes.py"
                )
                core.globals.close(-1)

    def script(self, root: Path, name: str):
        file = root / f'{name}.py'
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module

