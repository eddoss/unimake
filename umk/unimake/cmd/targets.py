import os

import asyncclick

from umk.unimake import root
from umk.unimake.utils import ConfigableGroup

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, core
    from umk.unimake import utils


@root.group(cls=ConfigableGroup, help="Project targets management commands")
@asyncclick.option("--remote", help="Execute command in specific remote environment")
@asyncclick.option("-R", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@asyncclick.pass_context
def targets(ctx: asyncclick.Context, remote: str, r: bool, c: tuple[str], p: tuple[str], f: bool):
    locally = not bool(remote or r)

    lo = runtime.LoadingOptions()
    lo.config.overrides = utils.parse_config_overrides(c)
    lo.config.presets = list(p)
    lo.config.file = f
    lo.modules.project = runtime.YES
    lo.modules.config = runtime.OPT
    lo.modules.remotes = runtime.NO if locally else runtime.NO
    runtime.load(lo)

    if not locally:
        rem = utils.find_remote(r, remote)
        rem.execute(cmd=["unimake", "project"] + utils.subcmd(ctx.invoked_subcommand))
        ctx.exit()


@targets.command(help="List project targets")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def ls(format: str):
    tars = runtime.container.targets
    if format == "style":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="", no_wrap=True)
        table.add_column("Description", justify="left", style="", no_wrap=True)
        for t in tars:
            table.add_row(t.name, t.description)
        core.globals.console.print(table)
    elif format == "json":
        data = [t.object().model_dump() for t in tars]
        core.globals.console.print_json(core.json.text(data))


@targets.command(name='inspect', help="Inspect targets details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
@asyncclick.argument('names', required=True, nargs=-1)
def inspect(format: str, names: tuple[str]):
    found = []
    for name in names:
        if name not in runtime.container.targets:
            core.globals.console.print(f"[yellow bold]Target '{name}' not found")
        else:
            found.append(name)
    objects = []
    for name in found:
        o = runtime.container.targets.get(name).object()
        objects.append(o)

    if format == "style":
        printer = utils.PropertiesPrinter()
        properties = []
        for o in objects:
            properties.append(o.properties)
        printer.print(*properties)

    elif format == "json":
        core.globals.console.print_json(core.json.text(objects))


