from umk.framework import config
from umk import core


@config.register
class Config(config.Config):
    class Build(core.Model):
        debug: bool = core.Field(
            default=True,
            description="Build binaries in debug mode"
        )
        all: bool = core.Field(
            default=False,
            description="Build all binaries"
        )

    class Docs(core.Model):
        enabled: bool = core.Field(
            default=False,
            description="Prepare documentation when build"
        )
        type: str = core.Field(
            default="pdf",
            description="Documentation type (pdf, html, xml)"
        )

    build: Build = Build()
    docs: Docs = Docs()


@config.preset
def release(c: Config):
    c.build.debug = False
    c.build.all = True
    c.docs.enabled = True
