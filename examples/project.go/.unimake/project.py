from umk.framework import project
from umk.framework.adapters import git, go, delve
from umk.framework.system import Environs


@project.register
class Project(project.Go):
    def __init__(self):
        super().__init__()
        self.layout = project.GoLayout()
        self.info.name.short = self.layout.root.name
        self.info.name.full = "Message Publisher"
        self.info.version = "v1.0.0"
        self.info.authors = [
            project.Author('Edward Sarkisyan', 'edw.sarkisyan@gmail.com')
        ]
        self.info.description.short = "Unimake project example (golang based)"
        self.go = go.Binary.find("1.18")
        self.dlv = delve.Binary.find()

    async def build(self,  mode: str):
        args = go.BuildArgs.new(mode=mode)
        args.output = self.layout.output / "app"
        args.sources.append(self.layout.cmd / "app")

        await self.go.build(args=args).asyn()

    def vendor(self):
        self.go.mod.tidy().sync()
        self.go.mod.vendor().sync()

    def debug(self,  port=2345):
        self.dlv.flags.port = port
        self.dlv.exec(self.layout.output / "app").sync()
