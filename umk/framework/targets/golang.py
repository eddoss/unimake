from umk import core
from umk.framework.adapters import go
from umk.framework.targets.interface import Interface


class GolangBinary(Interface):
    class Debug(core.Model):
        port: int = core.Field(
            default=2345,
            description="Port to run delve on"
        )

    tool: go.Go = core.Field(
        default_factory=go.Go,
        description="Golang tool object"
    )
    build: go.Build = core.Field(
        default_factory=go.Build,
        description="Build options"
    )
    debug: Debug = core.Field(
        default_factory=Debug,
        description="Debug options"
    )

    def object(self) -> core.Object:
        result = core.Object()
        result.type = "Target.GolangBinary"
        result.properties.new("Tool", self.tool.shell.cmd, "Golang tool object")
        result.properties.new("Build", " ".join(self.build.serialize()), "Build options")
        return result

    def run(self):
        self.tool.build(self.build)
