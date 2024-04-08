import os

import asyncclick

from umk.unimake.application import application
from umk.unimake.utils import ConfigableCommand

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core
    from umk.unimake import utils


@application.group(help="Config management commands")
def config():
    pass


@config.command(help="Remove saved config file")
def clean():
    if core.globals.paths.config.exists():
        os.remove(core.globals.paths.config)
        core.globals.console.print("[bold]Config file was removed")
    else:
        core.globals.console.print("[bold]Config file does not exists")


@config.command(cls=ConfigableCommand, help="Save project config")
@asyncclick.option("-c", required=False, type=str, multiple=True, help="Config entry override")
@asyncclick.option("-p", required=False, type=str, help="Config preset to apply")
def save(c: list[str], p: str):
    lo = runtime.LoadingOptions()
    lo.config.overrides = utils.parse_config_overrides(c)
    lo.config.preset = p or ""
    lo.modules.config = runtime.YES
    runtime.load(lo)

    runtime.container.config.save()


@config.command(name='inspect', help="Print default config details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def inspect(format: str):
    lo = runtime.LoadingOptions()
    lo.modules.config = runtime.YES
    runtime.load(lo)

    struct = runtime.container.config.instance.struct
    if not struct:
        core.globals.console.print(f"[bold]Config: config not found, register one at first !")
        return

    data = runtime.container.config.instance.object()
    if format == "style":
        printer = utils.PropertiesPrinter()
        printer.print(data.properties)
    elif format == "json":
        core.globals.console.print_json(
            json=core.json.text(data)
        )
