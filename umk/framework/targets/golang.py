import copy

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

    @staticmethod
    @core.typeguard
    def new(*, name: str, tool: go.Go, build: go.Build, port: int = 2345, label: str = "", description: str = "") -> tuple['GolangBinary', 'GolangBinary']:
        base = GolangBinary(
            name=name.strip(),
            label=label.strip(),
            description=description.strip(),
            tool=tool,
            build=build,
            debug=GolangBinary.Debug(port=port)
        )
        if not base.label:
            base.label = f"Binary '{base.name}'"
        if not base.description:
            base.description = f"Golang binary ({base.name})"

        debug = copy.deepcopy(base)
        debug.name = name
        debug.label += " (debug)"
        debug.build.flags.gc.append('all=-N')
        debug.build.flags.gc.append('-l')

        release = copy.deepcopy(base)
        release.name = name + ".release"
        release.label += " (release)"
        release.build.flags.gc.append('-dwarf=false')
        release.build.flags.ld.append('-s')
        release.build.flags.ld.append('-w')

        return debug, release

    def object(self) -> core.Object:
        result = super().object()
        result.type = "Target.GolangBinary"
        result.properties.new("Tool", self.tool.shell.cmd, "Golang tool object")
        result.properties.new("Build", " ".join(self.build.serialize()), "Build options")
        return result

    def run(self):
        self.tool.build(self.build)
