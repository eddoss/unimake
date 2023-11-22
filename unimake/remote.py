import sys
import asyncclick as click
import beartype
beartype.BeartypeConf.is_color = False
from asyncclick import Context
from rich.table import Table
from unimake import application
from umk.globals import Global
from umk import dotunimake as du
from umk.remote.register import find as find_remote
from umk.remote.register import iterate as iterate_remotes
from umk.remote.interface import Interface as RemoteInterface


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
    try:
        state = du.Unimake.load(
            root=Global.paths.unimake,
            env=du.Require.OPT,
            remotes=du.Require.YES,
        )
    except Exception as e:
        Global.console(
            f"[bold red]Unimake error !\n"
            f"Failed to load .unimake/remote.py: {e}"
        )
        sys.exit()
    if state != du.LoadingState.OK:
        du.LoadingStateMessages().on(state)
        sys.exit()

    # We don't need to find remote environment if 'ls' is requested.
    # If no subcommand was passed we assume it is 'ls'
    if ctx.invoked_subcommand in ('ls', ''):
        await ctx.invoke(ls)

    ctx.obj["instance"] = find_remote(name)
    if not ctx.obj["instance"]:
        if not name:
            Global.console.print(
                "[bold yellow]Could not find default remote! "
                "Please specify default remote in the '.unimake/remotes.py'"
            )
        else:
            Global.console.print(
                f"[bold yellow]Failed to find remote '{name}'! "
                f"Please specify it in the '.unimake/remotes.py'"
            )


@remote.command(name='build', help=RemoteInterface.build.__doc__)
@click.pass_context
def build(ctx: click.Context):
    ctx.obj.get("instance").build()


@remote.command(name='destroy', help=RemoteInterface.destroy.__doc__)
@click.pass_context
def destroy(ctx: click.Context):
    ctx.obj.get("instance").destroy()


@remote.command(name='up', help=RemoteInterface.up.__doc__)
@click.pass_context
def up(ctx: click.Context):
    ctx.obj.get("instance").up()


@remote.command(name='down', help=RemoteInterface.down.__doc__)
@click.pass_context
def down(ctx: click.Context):
    ctx.obj.get("instance").down()


@remote.command(name='shell', help=RemoteInterface.shell.__doc__)
@click.pass_context
def shell(ctx: click.Context):
    ctx.obj.get("instance").shell()


@remote.command(name='ls', help='List project remote environments')
def ls():
    table = Table(show_header=True, show_edge=True, show_lines=False)
    table.add_column("Name", justify="left", style="", no_wrap=True)
    table.add_column("Default", justify="center", style="", no_wrap=True)
    table.add_column("Description", justify="left", style="", no_wrap=True)
    for rem in iterate_remotes():
        default = ''
        if rem.default:
            default = 'x'
            table.add_row(f"{rem.name}", default, rem.description, style="yellow bold")
        else:
            table.add_row(rem.name, default, rem.description)
    Global.console.print(table)
    sys.exit()


@remote.command(name='exec', help=RemoteInterface.execute.__doc__)
@click.argument('program', required=True, nargs=1)
@click.argument('arguments', required=False, nargs=-1)
@click.pass_context
def execute(ctx: Context, program: str, arguments: tuple[str]):
    cmd = list(arguments)
    cmd.insert(0, program)
    rem: RemoteInterface = ctx.obj["instance"]
    rem.execute(cmd=cmd)
