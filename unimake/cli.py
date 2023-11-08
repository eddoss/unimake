import sys
import asyncclick as click
import beartype
beartype.BeartypeConf.is_color = False
from asyncclick import Context
from beartype.typing import Optional
from dataclasses import dataclass
from pathlib import Path
from rich.table import Table
from umk.globals import Global
from umk.cli.dot_unimake import DotUnimake
from umk.remote.register import find as find_remote
from umk.remote.register import iterate as iterate_remotes
from umk.remote.interface import Interface as RemoteInterface


@dataclass
class Common:
    unimake: DotUnimake = DotUnimake(Path())
    unimake_loading_error: Optional[Exception] = None
    no_unimake_folder: bool = False


common = Common()


@click.group(add_help_option=False, invoke_without_command=True)
async def application():
    pass


@application.command(name='help', help="Display help message")
def display_help_message():
    console = Global.console
    console.print("[blue bold]Welcome to the Unimake CLI :thumbs_up:\n")

    console.print("    [italic cyan bold]unimake <command> \[flags] \[arguments]")
    console.print("    [italic cyan bold]unimake <command> --help")
    console.print("    [italic cyan bold]unimake help")

    console.print("\nThis tool allows you to:")
    console.print("  • manage a umk extensions")
    console.print("  • initialize any project")
    console.print("  • and so on ...")

    if len(application.params):
        console.print(f"[bold underline]\nOptions")
        opts = Table(show_header=False, show_edge=False, show_lines=False, box=None)
        opts.add_column("", justify="left", style="yellow", no_wrap=True)
        opts.add_column("", justify="left", no_wrap=False)
        for param in application.params:
            opts.add_row('/'.join(param.opts), str(param.help))
        console.print(opts)

    if len(application.commands):
        console.print(f"[bold underline]\nCommands")
        cmds = Table(show_header=False, show_edge=False, show_lines=False, box=None)
        cmds.add_column("", justify="left", style="green bold", no_wrap=True)
        cmds.add_column("", justify="left", no_wrap=False)
        for _, command in application.commands.items():
            cmds.add_row(command.name, command.help)
        console.print(cmds)


@application.command(name='init', help="Initialize current directory as project")
def init():
    print(f"Call global: init")


@application.group(
    help="Remote environments management commands",
    invoke_without_command=True,
    # cls=GroupRemote
)
# @click.argument('name', required=False, default="", nargs=1)
@click.option('--name', '-n', default="")
@click.pass_context
async def remote(ctx: click.Context, name: str):
    # Validate '.unimake' existing and loading

    if common.no_unimake_folder:
        Global.console.print(
            "[bold] Call this command in the directory that contains '.unimake' folder"
        )
        sys.exit()

    if common.unimake_loading_error:
        Global.console.print(
            f"[bold red] Failed to load '.unimake': {common.unimake_loading_error}"
        )
        sys.exit()

    # No need to find remote environment if 'ls' is requested
    if ctx.invoked_subcommand in ('ls', ''):
        await ctx.invoke(remote_ls)

    # We can forward the 'remote' instance using ctx.obj,
    # so we need to create a context object

    ctx.ensure_object(dict)
    ctx.obj["interface"] = find_remote(name)
    if ctx.obj["interface"]:
        return

    if not name:
        Global.console.print(
            '[bold]Could not find default remote! '
            'Please specify default remote in .unimake/remotes.py'
        )
    else:
        Global.console.print(
            f"[bold red]Failed to find remote '{name}'! "
            f"Please specify it in '.unimake/remotes.py'"
        )

    sys.exit()


@remote.command(name='build', help=RemoteInterface.build.__doc__)
@click.pass_context
def remote_build(ctx: click.Context):
    ctx.obj.get("interface").build()


@remote.command(name='destroy', help=RemoteInterface.destroy.__doc__)
@click.pass_context
def remote_destroy(ctx: click.Context):
    ctx.obj.get("interface").destroy()


@remote.command(name='up', help=RemoteInterface.up.__doc__)
@click.pass_context
def remote_up(ctx: click.Context):
    ctx.obj.get("interface").up()


@remote.command(name='down', help=RemoteInterface.down.__doc__)
@click.pass_context
def remote_down(ctx: click.Context):
    ctx.obj.get("interface").down()


@remote.command(name='shell', help=RemoteInterface.shell.__doc__)
@click.pass_context
def remote_shell(ctx: click.Context):
    ctx.obj.get("interface").shell()


@remote.command(name='ls', help='List project remote environments')
def remote_ls():
    table = Table(show_header=False, show_edge=False, show_lines=False, box=None)
    table.add_column("", justify="left", style="green bold", no_wrap=True)
    table.add_column("", justify="left", no_wrap=False)
    for rem in iterate_remotes():
        if rem.default:
            table.add_row(f"*{rem.name}", rem.description, style="yellow bold")
        else:
            table.add_row(rem.name, rem.description)
    Global.console.print(table)
    sys.exit()


@remote.command(name='exec', help=RemoteInterface.execute.__doc__)
@click.argument('program', required=True, nargs=1)
@click.argument('arguments', required=False, nargs=-1)
@click.pass_context
def remote_exec(ctx: Context, program: str, arguments: tuple[str]):
    cmd = list(arguments)
    cmd.insert(0, program)
    rem: RemoteInterface = ctx.obj["interface"]
    rem.execute(cmd=cmd)
