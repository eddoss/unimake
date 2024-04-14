import sys
from importlib import util as importer
from pathlib import Path

from umk import framework, core
from umk.runtime.loading.config import Config
from umk.runtime.loading.project import Project
from umk.runtime.loading.targets import Targets


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

    def load(self, options: Options):
        root = options.root.expanduser().resolve().absolute()
        sys.path.insert(0, root.as_posix())

        config_found = (root / "config.py").exists()

        self.config.init()
        self.project.init()
        self.targets.init()

        if config_found:
            self.script(root, "config")
        self.script(root, "project")

        if config_found:
            self.config.setup(options.config)
        self.project.setup(self.config.instance)
        self.targets.setup(self.config.instance, self.project.instance)

    def script(self, root: Path, name: str):
        file = root / f'{name}.py'
        spec = importer.spec_from_file_location(name, file)
        module = importer.module_from_spec(spec)
        sys.modules[f'umk:{name}'] = module
        spec.loader.exec_module(module)
        self._modules[name] = module

