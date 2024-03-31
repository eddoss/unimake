from umk.framework import config


@config.register
class Config(config.Interface):
    with_docs = config.Entry(
        default=False,
        description="Build with docs or not"
    )
    debug = config.Entry(
        default=False,
        description="Build in debug mode"
    )


@config.preset
def dev():
    return {
        "with-docs": False,
        "debug": True
    }
