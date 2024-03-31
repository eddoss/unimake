import os

import asyncclick
import asyncclick as click

from umk.tools.unimake import application

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from umk.tools import utils
    from rich.table import Table
    from umk import runtime, framework, core


@application.group(
    help="Dependencies management commands",
    invoke_without_command=False,
    no_args_is_help=True,
    add_help_option=True,
)
@click.option("--remote", default=None, help="Execute command in specific remote environment")
@click.option("-R", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@click.pass_context
def depends(ctx: asyncclick.Context, remote: str, r: bool):
    locally = not bool(remote or r)
    runtime.load(
        root=core.globals.paths.unimake,
        project=runtime.YES,
        config=runtime.OPT,
        remotes=[runtime.YES, runtime.NO][int(locally)]
    )
    if not locally:
        rem = utils.find_remote(r, remote)
        rem.execute(cmd=["unimake", "depends"] + utils.subcmd(ctx.invoked_subcommand))
        ctx.exit()


@depends.command(help="List dependency groups")
@click.option('--format', '-f', default="style", type=click.Choice(["style", "json", "yaml"], case_sensitive=False), help="Output format")
def groups(format: str):
    deps = framework.project.get().dependencies

    if format == "style":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="bold", no_wrap=True)
        table.add_column("Description", justify="left", style="italic", no_wrap=True)
        for group in deps.groups():
            table.add_row(group.name, group.description or "<empty>")
        core.globals.console.print(table)
        return

    data = [{"name": group.name, "description": group.description} for group in deps.groups()]
    if format == "json":
        core.globals.console.print_json(core.json.text(data))
    elif format == "yaml":
        core.globals.console.print(core.yaml.text({"groups": data}))


@depends.command(help="Resolve dependencies (or specific group)")
@click.option('--groups', '-g', multiple=True, help="Groups to deal with")
def resolve(groups: list[str]):
    deps = framework.project.get().dependencies
    if not groups:
        deps.resolve()
    else:
        found = []
        for group in groups:
            if group not in deps:
                core.globals.console.print(f"[bold yellow]Group not found:[/] '{group}'")
            else:
                found.append(group)
        for name in found:
            group = deps[name]
            group.resolve()


@depends.command(help="Inspect dependency groups/group/item")
@click.option('--format', '-f', default="style", type=click.Choice(["style", "json", "yaml"], case_sensitive=False), help="Output format")
def inspect():
    pass
