import os

import asyncclick

from umk.application.cmd import root
from umk.application import utils

if not os.environ.get('_UMK_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, core
    from umk.application.printers import PropertiesPrinter


@root.group(help="Project targets management commands")
@utils.options.config.all
def target(c: tuple[str], p: tuple[str], f: bool):
    opt = runtime.Options()
    opt.config = utils.config(f, p, c)
    runtime.c.load(opt)


@target.command(help="List project targets")
@utils.options.style
def ls(s: str):
    if s == "style":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="", no_wrap=True)
        table.add_column("Description", justify="left", style="", no_wrap=True)
        for t in runtime.c.targets:
            table.add_row(t.name, t.description)
        core.globals.console.print(table)
    elif s == "json":
        data = [t.object().model_dump() for t in runtime.c.targets]
        core.globals.console.print_json(core.json.text(data))


@target.command(name='inspect', help="Inspect targets details")
@utils.options.style
@asyncclick.argument('names', required=True, nargs=-1)
def inspect(s: str, names: tuple[str]):
    found = []
    for name in names:
        if name not in runtime.c.targets:
            core.globals.console.print(f"[yellow bold]Target '{name}' not found")
        else:
            found.append(name)
    objects = []
    for name in found:
        o = runtime.c.targets.get(name).object()
        objects.append(o)

    if s == "style":
        printer = PropertiesPrinter()
        properties = []
        for o in objects:
            properties.append(o.properties)
        printer.print(*properties)

    elif s == "json":
        core.globals.console.print_json(core.json.text(objects))
