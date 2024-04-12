import os

import asyncclick

from umk.application.root import root
from umk.application.utils import ConfigableGroup

if not os.environ.get('_UMK_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core
    from umk.application import utils


@root.group(cls=ConfigableGroup, help="Project management commands")
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
    framework.project.release()


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


@project.command(name='inspect', help="Print project details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def inspect(format: str):
    pro = runtime.container.project.object
    tar: list[framework.targets.Interface] = runtime.container.targets
    act = runtime.container.project.actions
    if format in ("style", ""):
        table_info = Table(
            title="INFO",
            title_style="bold cyan",
            title_justify="left",
            show_header=False,
            show_edge=False,
            show_lines=False,
            box=None,
        )
        table_info.add_column("Name", justify="left", style="bold", no_wrap=True)
        table_info.add_column("Value", justify="left", style="", no_wrap=True)
        table_info.add_row("• Id", pro.info.id)
        table_info.add_row("• Version", pro.info.version)
        table_info.add_row("• Name", pro.info.name)
        table_info.add_row("• Description", pro.info.description)

        if pro.info.contributors:
            table_contributors = Table(
                title="CONTRIBUTORS",
                title_style="bold cyan",
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
                table_contributors.add_row(f"• {contrib.name}", contacts)

        if act:
            table_actions = Table(
                title="ACTIONS",
                title_style="bold cyan",
                title_justify="left",
                show_header=False,
                show_edge=False,
                show_lines=False,
                box=None,
            )
            table_actions.add_column("Name", justify="left", style="bold", no_wrap=True)
            table_actions.add_column("Description", justify="left", style="", no_wrap=True)
            for n, a in runtime.container.project.actions.items():
                d = (a.__doc__ or "").strip()
                table_actions.add_row(f"• {n}", d)

        if tar:
            table_targets = Table(
                title="TARGETS",
                title_style="bold cyan",
                title_justify="left",
                show_header=False,
                show_edge=False,
                show_lines=False,
                box=None,
            )
            table_targets.add_column("Name", justify="left", style="bold", no_wrap=True)
            table_targets.add_column("Description", justify="left", style="", no_wrap=True)
            for t in tar:
                table_targets.add_row(f"• {t.name}", t.description)
        core.globals.console.print(table_info)
        if act:
            core.globals.console.print()
            core.globals.console.print(table_actions)
        if tar:
            core.globals.console.print()
            core.globals.console.print(table_targets)
        if pro.info.contributors:
            core.globals.console.print()
            core.globals.console.print(table_contributors)
    elif format == "json":
        # TODO Append actions and targets
        # data = {
        #     "info": pro.info.object(),
        #     "actions:"
        # }
        # if tar:
        #     data.append()
        core.globals.console.print_json(core.json.text(pro.info))


