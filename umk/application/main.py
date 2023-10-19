import beartype
beartype.BeartypeConf.is_color = False

import inspect
import asyncio
import sys
import dotenv
import asyncclick as click

from beartype.typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from pathlib import Path
from umk.application.config import Global, Config
from umk.application.modules import ExternalModules


console = Console()
external: Optional[ExternalModules] = None


def show_native_help():
    console = Console()
    console.print("[blue bold]Welcome to the Umimake :thumbs_up:\n")

    console.print("    [white]Run native command     [/][italic cyan bold]umk /<command> \[flags] \[arguments]")
    console.print("    [white]Get native help        [/][italic cyan bold]umk /help")
    console.print("    [white]Run project command    [/][italic cyan bold]umk <command> \[flags] \[arguments]")
    console.print("    [white]Get project help       [/][italic cyan bold]umk help")
    console.print("    [white]Get command help       [/][italic cyan bold]umk /<command> --help")

    console.print("\nThis tool allows you to quickly and easily:")
    console.print("  • describe the project maintaining steps")
    console.print("  • create a convenient CLI to call this steps")

    console.print("\nUnimake CLI has 2 layers of the commands:")
    console.print("  • [bold]native[/bold] - commands of the Unimake itself")
    console.print("  • [bold]external[/bold] - commands of the current project")

    console.print("\nNative commands starts with '/'.")
    console.print("External commands has arbitrary names.")

    console.print(f"[bold underline]\nNative options")
    opts = Table(show_header=False, show_edge=False, show_lines=False, box=None)
    opts.add_column("", justify="left", style="yellow", no_wrap=True)
    opts.add_column("", justify="left", no_wrap=False)
    for param in application.params:
        opts.add_row('/'.join(param.opts), param.help)
    console.print(opts)

    console.print(f"[bold underline]\nNative commands")
    cmds = Table(show_header=False, show_edge=False, show_lines=False, box=None)
    cmds.add_column("", justify="left", style="green bold", no_wrap=True)
    cmds.add_column("", justify="left", no_wrap=False)
    for _, command in application.commands.items():
        if command.name.startswith('/'):
            cmds.add_row(command.name, command.help)
    console.print(cmds)

    console.print("\nRun '/<command> --help' to get the command details")


def show_external_help():
    info = external.project.project.info
    console = Console()
    console.print(f"[blue bold]Welcome to the project[/] [bold yellow]{info.name.full or info.name.short}\n")

    console.print("    [white]Basic usage     [/][italic cyan bold]umk <command> \[flags] \[arguments]")
    console.print("    [white]Command help    [/][italic cyan bold]umk <command> --help")
    console.print("    [white]Project help    [/][italic cyan bold]umk help")
    console.print("    [white]Native help     [/][italic cyan bold]umk /help")

    if info.description:
        console.print(f"\n{info.description}")

    console.print(f"[bold underline]\nProject commands")
    cmds = Table(show_header=False, show_edge=False, show_lines=False, box=None)
    cmds.add_column("", justify="left", style="green bold", no_wrap=True)
    cmds.add_column("", justify="left", no_wrap=False)
    for _, command in application.commands.items():
        if not command.name.startswith('/'):
            cmds.add_row(command.name, command.help)
    console.print(cmds)


def show_project_not_found_error():
    code ="""
class Project(umk.GoProject):
    def __init__():
        super().__init__()
        project.info.name.short = 'super-project'
        project.info.name.full = 'Super mega project'
        project.info.description = 'Super project description'

project = Project()
"""
    console.print("[bold red]Unimake error: instance of the 'Project' was not found !")
    console.print("[bold red]File [underline]'.unimake/project.py'[/underline] must contains instance of the Project")
    console.print(Syntax(code, "python", theme='monokai', line_numbers=False))


@click.group(add_help_option=False, invoke_without_command=True)
@click.option('--remote', '-r', default='', help="Execute command in remote environment (ignored in native)")
@click.pass_context
def application(ctx: click.Context, remote: str):
    if not Global.paths.work.exists():
        if ctx.invoked_subcommand in ('', None):
            show_native_help()
            click.Abort()
        elif not ctx.invoked_subcommand.startswith('/'):
            console.print("[bold]Current directory is not a Unimake project")
            console.print("[bold]To create a project run:")
            console.print("[bold cyan]    umk /init ...")
            console.print("[bold]To get init details run:")
            console.print("[bold cyan]    umk /init --help")
            click.Abort()
    Global.remote = remote


@application.command(name='/help', help="Display help message")
def display_native_help():
    show_native_help()


@application.command(name='/init', help="Initialize current directory as project")
def init():
    print(f"Call global: init")


def cmd(*args: Any, **kwargs):
    return application.command(*args, **kwargs)


def run():
    try:
        asyncio.run(application())
    except Exception:
        console.print_exception(show_locals=False, max_frames=1)


def main():
    global external
    global need_print_help

    Global.paths = Config.Paths(Path.cwd().expanduser().resolve().absolute())
    # validate_paths()

    if not Global.paths.work.exists():
        run()
        return

    if not Global.paths.work.is_dir():
        console.print(f"[bold red]Unimake error !")
        console.print(f"[bold red]Found '.unimake' but it's not a folder")
        console.print(f"[bold red]Try to remove '.unimake' at first and init a project:")
        console.print(f"[bold red]    umk /init ...")
        console.print(f"[bold red]To get init details run:")
        console.print(f"[bold red]    umk /init --help")
        sys.exit()

    if not Global.paths.cli.is_file() or not Global.paths.project.is_file():
        console.print(f"[bold bold red]Unimake error")
        console.print(f"[bold bold red]Found '.unimake', but it's broken !")
        console.print(f"[bold bold red]This folder must contains files:")
        console.print(f"[bold bold red]  - project.py")
        console.print(f"[bold bold red]  - cli.py")
        sys.exit()

    if Global.paths.dotenv:
        try:
            dotenv.load_dotenv(Global.paths.dotenv)
        except Exception:
            console.print_exception(show_locals=False, max_frames=1)

    try:
        external = ExternalModules(Global.paths.work)
    except Exception:
        console.print_exception(show_locals=False, max_frames=1)
        return

    if not (hasattr(external.project, 'project')):
        show_project_not_found_error()
        return

    for o in external.cli.module.__dict__.values():
        if isinstance(o, click.Command):
            application.add_command(o)

    if not (hasattr(external.cli.module, 'show_help') and inspect.isfunction(external.cli.show_help)):
        @application.command(name='help', help="Display help message")
        def display_external_help():
            show_external_help()
    run()


if __name__ == '__main__':
    main()
