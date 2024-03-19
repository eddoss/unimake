from umk.framework import project
from umk.framework.adapters import go, Delve


@project.register
class Project(project.Golang):
    def __init__(self):
        super().__init__()
        self.layout = project.GolangLayout()
        self.info.id = "go-example"
        self.info.name = self.info.id
        self.info.description = "Unimake project example (golang based)"
        self.info.version = "v1.0.0"
        self.info.authors = [
            project.Author(name='Edward Sarkisyan', email=['edw.sarkisyan@gmail.com'])
        ]
        self.go = go.Go()
        self.dlv = Delve()

    async def build(self, mode: str):
        options = go.Build.new(
            mode,
            self.layout.output / self.info.name,
            self.layout.cmd / self.info.name
        )
        await self.go.build(options).asyn()

    def vendor(self):
        self.go.mod.tidy().sync()
        self.go.mod.vendor().sync()

    def debug(self, port=2345):
        self.dlv.flags.port = port
        self.dlv.exec(cmd=[self.layout.output / self.info.name]).sync()
