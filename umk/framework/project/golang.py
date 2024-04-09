from umk import core
from umk.framework.project.base import Layout
from umk.framework.project.base import Scratch
from umk.framework.adapters import go
from umk.framework import targets


class GolangLayout(Layout):
    @property
    def assets(self): return self.root / "assets"

    @property
    def build(self): return self.root / "build"

    @property
    def cmd(self): return self.root / "cmd"

    @property
    def configs(self): return self.root / "configs"

    @property
    def deployment(self): return self.root / "deployment"

    @property
    def docs(self): return self.root / "docs"

    @property
    def examples(self): return self.root / "examples"

    @property
    def githooks(self): return self.root / "githooks"

    @property
    def init(self): return self.root / "init"

    @property
    def internal(self): return self.root / "internal"

    @property
    def pkg(self): return self.root / "pkg"

    @property
    def scripts(self): return self.root / "scripts"

    @property
    def test(self): return self.root / "test"

    @property
    def third_party(self): return self.root / "third_party"

    @property
    def tools(self): return self.root / "tools"

    @property
    def vendor(self): return self.root / "vendor"

    @property
    def web(self): return self.root / "web"

    @property
    def website(self): return self.root / "website"

    @property
    def output(self): return self.root / "output"


class GolangBinary(Scratch):
    def __init__(self):
        super().__init__()
        self.layout: GolangLayout = GolangLayout()
        self.tool: go.Go = go.Go()

    def binary(self):
        required = (
            targets.GolangBinary,
        )
        container: list[targets.Interface] = []
        for target in self.targets:
            if not issubclass(type(target), required):
                continue
            container.append(target)
        if not targets:
            core.globals.console.print(
                "[bold]No targets to build !"
            )
            return
        for target in container:
            target.run()
