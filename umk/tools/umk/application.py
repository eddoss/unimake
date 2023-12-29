import sys
import asyncclick
from rich.table import Table
from umk.framework.project import BaseProject
from umk import framework, dot, globals

Sections = dict[framework.cli.Section, list[asyncclick.Command]]
DefaultSection = framework.cli.Section(name='Default', description='Default commands')
RegisteredSections: Sections = {DefaultSection: []}


class Command(asyncclick.Command):
    def __init__(self, section: framework.cli.Section = DefaultSection, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        global RegisteredSections
        if section not in RegisteredSections:
            RegisteredSections[section] = [self]
        else:
            RegisteredSections[section].append(self)


class Group(asyncclick.Group):
    command_class = Command


class HelpMessage:
    def render(self, project: BaseProject, section: Sections):
        console = globals.console
        info = project.info
        console.print(f"[blue bold]Welcome to[/] [bold yellow]{info.name.full or info.name.short}\n")

        console.print("    [italic cyan bold]umk <command> \[flags] \[arguments]")
        console.print("    [italic cyan bold]umk <command> --help")
        console.print("    [italic cyan bold]umk help")

        if info.description:
            console.print(f"\n{info.description.short}")

        for section, commands in section.items():
            console.print(f"[bold underline]\n{section.name}")
            cmds = Table(show_header=False, show_edge=False, show_lines=False, box=None)
            cmds.add_column("", justify="left", style="green bold", no_wrap=True)
            cmds.add_column("", justify="left", no_wrap=False)
            for command in commands:
                cmds.add_row(command.name, command.help)
            console.print(cmds)


Helper = HelpMessage()


@asyncclick.group(
    cls=Group,
    add_help_option=False,
    invoke_without_command=False,
)
@asyncclick.option(
    '--remote',
    default='',
    help="Execute command in specific remote environment"
)
@asyncclick.option(
    "-r",
    is_flag=True,
    default=False,
    help="Execute command in default remote environment."
         "This flag has higher priority than --remote"
)
@asyncclick.pass_context
def application(ctx: asyncclick.Context, remote: str, r: bool):
    # Skip remote execution if did not specify one

    default_remote = r
    specific_remote = remote
    if not default_remote and not specific_remote:
        return

    # Find remote environment if specified

    rem = framework.remote.find("" if default_remote else specific_remote)
    if default_remote and not rem:
        globals.console.print(
            '[bold red]Failed to find default remote environment! '
            'Please specify it in the .unimake/remotes.py'
        )
        sys.exit()
    elif not rem and specific_remote:
        globals.console.print(
            f"[bold red]Failed to find remote environment '{specific_remote}'! "
            f"Please create it in the .unimake/remotes.py"
        )
        sys.exit()

    # Parse subcommand and its arguments

    subcmd = sys.argv[sys.argv.index(ctx.invoked_subcommand) + 1:]
    subcmd.insert(0, ctx.invoked_subcommand)
    subcmd.insert(0, 'umk')

    # We skip rem.build() and rem.up() because remote environment must be built
    # and started by unimake tool. We need just run the command.

    rem.execute(cmd=subcmd)


@application.command(name='help', help="Display help message", section=DefaultSection)
def display_help_message():
    Helper.render(dot.Instance.project, RegisteredSections)
