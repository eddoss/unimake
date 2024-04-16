import os

import asyncclick

from umk.application.cmd import root
from umk.application import utils

if not os.environ.get('_UMK_COMPLETE', None):
    from umk import runtime, core
    from umk.application.printers import PropertiesPrinter


@root.group(help="Config management commands")
def config():
    pass


@config.command(help="Remove saved config file")
def clean():
    runtime.c.config.clean()


@config.command(help="Save project config")
@utils.options.config.preset
@utils.options.config.entry
def save(c: tuple[str], p: tuple[str]):
    opt = runtime.Options()
    opt.config = utils.config(False, p, c)
    runtime.c.load(opt)
    runtime.c.config.save()


@config.command(help="Write entry inside config file")
@asyncclick.argument('values', required=True, nargs=-1)
def write(values: tuple[str]):
    opt = runtime.Options()
    opt.config.file = True
    runtime.c.load(opt)
    entries = utils.config(False, None, values).overrides
    runtime.c.config.write(entries)


@config.command(help="Print config presets")
@utils.options.style
def presets(s: str):
    opt = runtime.Options()
    runtime.c.load(opt)

    if not runtime.c.config.presets:
        core.globals.console.print(f"[bold]Config presets not found !")
        return

    data = {name: func.__doc__ or "" for name, func in runtime.c.config.presets.items()}
    if s == "style":
        properties = core.Properties()
        for name, desc in data.items():
            properties.new(name=name, desc=desc, value=None)
        printer = PropertiesPrinter()
        printer.print(properties, value=False)
    elif s == "json":
        core.globals.console.print_json(
            json=core.json.text(data)
        )


@config.command(name='inspect', help="Print default config details")
@utils.options.style
@utils.options.config.all
def inspect(s: str, c: tuple[str], p: tuple[str], f: bool):
    opts = runtime.Options()
    opts.config = utils.config(f, p, c)
    runtime.c.load(opts)

    conf = runtime.c.config
    if not conf.instance:
        core.globals.console.print(f"[bold]Config: config not found, register one at first !")
        return

    data = conf.object()
    if s == "style":
        printer = PropertiesPrinter()
        printer.print(data.properties)
    elif s == "json":
        core.globals.console.print_json(
            json=core.json.text(data)
        )
