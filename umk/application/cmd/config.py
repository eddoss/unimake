import os

import asyncclick

from umk.application.cmd import root
from umk.application.utils import ConfigableCommand

if not os.environ.get('_UMK_COMPLETE', None):
    from umk import runtime, core
    from umk.application import utils


@root.group(help="Config management commands")
def config():
    pass


@config.command(help="Remove saved config file")
def clean():
    runtime.c.config.clean()


@config.command(help="Save project config")
@asyncclick.option("-C", required=False, type=str, multiple=True, help="Config entry override")
@asyncclick.option("-P", required=False, type=str, multiple=True, help="Config preset to apply")
def save(c: tuple[str], p: tuple[str]):
    opt = runtime.Options()
    opt.config.overrides = utils.parse_config_overrides(c)
    opt.config.presets = list(p)
    runtime.c.load(opt)

    runtime.c.config.save()


@config.command(help="Write entry inside config file")
@asyncclick.argument('values', required=True, nargs=-1)
def write(values: tuple[str]):
    opt = runtime.Options()
    opt.config.file = True
    runtime.c.load(opt)

    entries = utils.parse_config_overrides(values)
    runtime.c.config.write_entries(entries)


@config.command(help="Print config presets")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def presets(format: str):
    opt = runtime.Options()
    runtime.c.load(opt)

    if not runtime.c.config.presets:
        core.globals.console.print(f"[bold]Config presets not found !")
        return

    data = {name: func.__doc__ or "" for name, func in runtime.c.config.presets.items()}
    if format == "style":
        properties = core.Properties()
        for name, desc in data.items():
            properties.new(name=name, desc=desc, value=None)
        printer = utils.PropertiesPrinter()
        printer.print(properties, value=False)
    elif format == "json":
        core.globals.console.print_json(
            json=core.json.text(data)
        )


@config.command(cls=ConfigableCommand, name='inspect', help="Print default config details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def inspect(format: str, c: tuple[str], p: tuple[str], f: bool):
    opts = runtime.Options()
    opts.config.file = f
    opts.config.presets = list(p)
    opts.config.overrides = utils.parse_config_overrides(c)
    runtime.c.load(opts)

    conf = runtime.c.config
    if not conf.instance:
        core.globals.console.print(f"[bold]Config: config not found, register one at first !")
        return

    data = conf.object()
    if format == "style":
        printer = utils.PropertiesPrinter()
        printer.print(data.properties)
    elif format == "json":
        core.globals.console.print_json(
            json=core.json.text(data)
        )
