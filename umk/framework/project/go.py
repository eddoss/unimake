from umk.framework.project.base import Layout as BaseLayout
from umk.framework.project.scratch import Scratch
from umk import globals


class Layout(BaseLayout):
    def __init__(self, root=globals.paths.work):
        super().__init__(root)
        self.assets = self.root / "assets"
        self.build = self.root / "build"
        self.cmd = self.root / "cmd"
        self.configs = self.root / "configs"
        self.deployment = self.root / "deployment"
        self.docs = self.root / "docs"
        self.examples = self.root / "examples"
        self.githooks = self.root / "githooks"
        self.init = self.root / "init"
        self.internal = self.root / "internal"
        self.pkg = self.root / "pkg"
        self.scripts = self.root / "scripts"
        self.test = self.root / "test"
        self.third_party = self.root / "third_party"
        self.tools = self.root / "tools"
        self.vendor = self.root / "vendor"
        self.web = self.root / "web"
        self.website = self.root / "website"
        self.output = self.root / "output"


class Project(Scratch):
    def __init__(self):
        super().__init__()
        self.layout = Layout()
