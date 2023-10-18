import sys
from importlib import util as importer
from pathlib import Path


class Module:
    def __init__(self, name: str, file: Path):
        spec = importer.spec_from_file_location(name, file.expanduser().resolve().absolute().as_posix())
        self.module = importer.module_from_spec(spec)
        sys.modules[name] = self.module
        spec.loader.exec_module(self.module)

    def __getattr__(self, key):
        return self.module.__dict__[key]


class ExternalModules:
    def __init__(self, root: Path):
        sys.path.insert(0, root.as_posix())
        self.project = Module('umk:external:project', root / 'project.py')
        self.cli = Module('umk:external:cli', root / 'cli.py')