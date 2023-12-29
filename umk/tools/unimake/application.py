import asyncclick as click
from rich.table import Table
from umk import globals


@click.group(add_help_option=False, invoke_without_command=True)
async def application():
    pass


@application.command(name='help', help="Display help message")
def display_help_message():
    console = globals.console
    console.print("[blue bold]Welcome to the Unimake CLI :thumbs_up:\n")

    console.print("    [italic cyan bold]unimake <command> \[flags] \[arguments]")
    console.print("    [italic cyan bold]unimake <command> --help")
    console.print("    [italic cyan bold]unimake help")

    console.print("\nThis tool allows you to:")
    console.print("  • manage a umk extensions")
    console.print("  • initialize any project")
    console.print("  • call remote environment commands")
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