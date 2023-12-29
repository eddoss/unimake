from umk.framework import project


class Layout(project.BaseLayout):
    def __init__(self):
        super().__init__()
        self.docs = self.root / "docs"
        self.dev = self.root / "development"
        self.src = self.root / "umk"
        self.tests = self.root / "tests"
        self.examples = self.root / "examples"
        self.dist = self.root / "dist"
