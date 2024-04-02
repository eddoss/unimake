from umk.framework import config
from umk import core


@config.register
class Config(config.Config):
    class Build(core.Model):
        debug: bool = True
        all: bool = False

    class Docs(core.Model):
        enabled: bool = False
        type: str = "pdf"

    build: Build = Build()
    docs: Docs = Docs()


@config.preset
def release():
    return {
        "build.debug": False,
        "build.all": True,
        "docs.enabled": True,
    }
