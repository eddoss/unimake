import beartype
beartype.BeartypeConf.is_color = False

import asyncio
import asyncclick as click

from beartype.typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from pathlib import Path


console = Console()


@click.group(add_help_option=False, invoke_without_command=True)
@click.pass_context
async def application(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        await display_help_message.invoke(ctx)
        click.Abort()


@application.command(name='help', help="Display help message")
def display_help_message():
    console = Console()
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


def entrypoint():
    try:
        asyncio.run(application())
    except Exception:
        console.print_exception(show_locals=False, max_frames=1)


if __name__ == '__main__':
    entrypoint()
