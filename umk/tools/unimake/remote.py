import os

import asyncclick as click
from asyncclick import Context

from umk.tools.unimake import application

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import dot, framework, core


@application.group(
    help="Remote environments management commands",
    invoke_without_command=True,
    no_args_is_help=True,
    add_help_option=True,
)
@click.option('--name', '-n', default="", help="Remote environment name")
@click.pass_context
async def remote(ctx: click.Context, name: str):
    ctx.ensure_object(dict)
    ctx.obj["instance"] = None  # remote environment instance

    # Load .unimake/remotes.py
    dot.Instance.load(root=core.globals.paths.unimake, remotes=dot.YES, project=dot.OPT)

    # We don't need to find remote environment if 'ls' is requested.
    # If no subcommand was passed we assume it is 'ls'
    if ctx.invoked_subcommand in ('ls', ''):
        await ctx.invoke(ls)

    ctx.obj["instance"] = framework.remote.find(name)
    if not ctx.obj["instance"]:
        if not name:
            core.globals.console.print(
                "[bold yellow]Could not find default remote! "
                "Please specify default remote in the '.unimake/remotes.py'"
            )
        else:
            core.globals.console.print(
                f"[bold yellow]Failed to find remote '{name}'! "
                f"Please specify it in the '.unimake/remotes.py'"
            )
        core.globals.close(-1)


@remote.command(name='build', help="Build remote environment")
@click.pass_context
def build(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.build()


@remote.command(name='destroy', help="Destroy remote environment")
@click.pass_context
def destroy(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.destroy()


@remote.command(name='up', help="Start remote environment")
@click.pass_context
def up(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.up()


@remote.command(name='down', help="Stop remote environment")
@click.pass_context
def down(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.down()


@remote.command(name='shell', help="Open remote environment shell")
@click.pass_context
def shell(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.shell()


@remote.command(name='ls', help='List project remote environments')
def ls():
    table = Table(show_header=True, show_edge=True, show_lines=False)
    table.add_column("Name", justify="left", style="", no_wrap=True)
    table.add_column("Default", justify="center", style="", no_wrap=True)
    table.add_column("Description", justify="left", style="", no_wrap=True)
    for rem in framework.remote.iterate():
        default = ''
        if rem.default:
            default = 'x'
            table.add_row(f"{rem.name}", default, rem.description, style="yellow bold")
        else:
            table.add_row(rem.name, default, rem.description)
    core.globals.console.print(table)
    core.globals.close()


@remote.command(name='exec', help="Execute command in remote environment")
@click.argument('program', required=True, nargs=1)
@click.argument('arguments', required=False, nargs=-1)
@click.pass_context
def execute(ctx: Context, program: str, arguments: tuple[str]):
    cmd = list(arguments)
    cmd.insert(0, program)
    rem: framework.remote.Interface = ctx.obj.get("instance")
    rem.execute(cmd=cmd)


@remote.command(name='inspect', help='Show remote environment details')
@click.option('--format', '-f', default="table", type=click.Choice(["table", "json", "yaml"], case_sensitive=False), help="Output format")
@click.pass_context
def inspect(ctx: Context, format: str):
    rem: framework.remote.Interface = ctx.obj.get("instance")
    if format == "table" or format == "":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="", no_wrap=True)
        table.add_column("Description", justify="left", style="", no_wrap=True)
        table.add_column("Value", justify="left", style="", no_wrap=True)
        for prop in rem.properties():
            table.add_row(prop.name, prop.description, str(prop.value))
        core.globals.console.print(table)

    data = [prop.model_dump() for prop in rem.properties()]
    if format == "json":
        core.globals.console.print_json(core.json.text(data))
    elif format in ("yml", "yaml"):
        core.globals.console.print(core.yaml.text({"properties": data}))


@remote.command(name='upload', help="Upload files to remote environment")
@click.argument('items', required=False, nargs=-1)
@click.pass_context
def upload(ctx: Context, items: tuple[str]):
    rem: framework.remote.Interface = ctx.obj.get("instance")
    paths = split(items)
    if not paths:
        return
    rem.upload(paths)


@remote.command(name='download', help="Download files from remote environment")
@click.argument('items', required=False, nargs=-1)
@click.pass_context
def download(ctx: Context, items: tuple[str]):
    rem: framework.remote.Interface = ctx.obj.get("instance")
    paths = split(items)
    if not paths:
        return
    rem.download(paths)


def split(items: tuple[str]) -> dict[str, str]:
    def error():
        core.globals.console.print("[bold red]Invalid upload/download item!")
        core.globals.console.print("[bold red]Pattern")
        core.globals.console.print("[bold red]    upload:   <local/file>:<remote/file>")
        core.globals.console.print("[bold red]    download: <remote/file>:<local/file>")
    result = {}
    for item in items:
        if ':' not in item:
            error()
            return {}
        s = item.split(':')
        result[s[0]] = s[1]
    return result
