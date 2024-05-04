from umk import core
from umk.kit import config


@config.register
class Config(config.Interface):
    class Debug(core.Model):
        on: bool = core.Field(False, description="Enable debug info")
        port: int = core.Field(default=2345, description="Port to start debugger on")
    debug: Debug = core.Field(default_factory=Debug)
    usermod: bool = core.Field(True, description="Create user inside development container")


@config.preset(name="local")
def _(s: Config):
    s.debug.port = 2020
