import os

import asyncclick

from umk.unimake.application import application
from umk.unimake.utils import ConfigableGroup

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core
    from umk.unimake import utils


@application.group(cls=ConfigableGroup, help="Project management commands")
@asyncclick.option("--remote", help="Execute command in specific remote environment")
@asyncclick.option("-R", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@asyncclick.pass_context
def project(ctx: asyncclick.Context, remote: str, r: bool, c: tuple[str], p: tuple[str], f: bool):
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


@project.command(help="Release project")
def release():
    framework.project.run('release')


@project.command(help="List project actions")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def actions(format: str):
    data = core.Object()
    data.type = "Project.Actions"
    for n, a in runtime.container.project.actions.items():
        data.properties.new(name=n, value="", desc=(a.__doc__ or "").strip())
    if format == "style":
        printer = utils.PropertiesPrinter()
        printer.print(data.properties, value=False)
    elif format == "json":
        core.globals.console.print_json(core.json.text(data))


@project.command(help="List project targets")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def targets(format: str):
    objects = runtime.container.targets.objects()
    if format == "style":
        printer = utils.PropertiesPrinter()
        for data in objects:
            printer.print(data.properties)
    elif format == "json":
        core.globals.console.print_json(core.json.text(objects))


@project.command(name='inspect', help="Print project details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def inspect(format: str):
    pro = runtime.container.project.object
    if format in ("style", ""):
        table_info = Table(
            title="INFO",
            title_style="bold",
            title_justify="left",
            show_header=False,
            show_edge=False,
            show_lines=False,
            box=None,
        )
        table_info.add_column("Name", justify="left", style="bold", no_wrap=True)
        table_info.add_column("Value", justify="left", style="", no_wrap=True)
        table_info.add_row("Id", pro.info.id)
        table_info.add_row("Version", pro.info.version)
        table_info.add_row("Name", pro.info.name)
        table_info.add_row("Description", pro.info.description)

        if pro.info.contributors:
            table_contributors = Table(
                title="CONTRIBUTORS",
                title_style="bold",
                title_justify="left",
                show_header=False,
                show_edge=False,
                show_lines=False,
                box=None,
            )
            table_contributors.add_column("Name", justify="left", style="bold", no_wrap=True)
            table_contributors.add_column("Value", justify="left", style="", no_wrap=True)
            for contrib in pro.info.contributors:
                contacts = " ".join(contrib.email)
                contacts += " " + " ".join([f'{k}:{v}' for k, v in contrib.socials.items()])
                table_contributors.add_row(contrib.name, contacts)

        core.globals.console.print(table_info)
        core.globals.console.print()
        if pro.info.contributors:
            core.globals.console.print(table_contributors)
    elif format == "json":
        core.globals.console.print_json(core.json.text(pro.info))


