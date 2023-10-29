import asyncclick
from beartype import beartype
from beartype.typing import Optional
from rich.table import Table
from umk.globals import Global
from umk.project import Project
from umk.cli.sections import Section
from umk.cli.dot_unimake import DotUnimake


Sections = dict[Section, list[asyncclick.Command]]
DefaultSection = Section(name='Default', description='Default commands')
RegisteredSections: Sections = {DefaultSection: []}
Unimake: Optional[DotUnimake] = None


class Command(asyncclick.Command):
    def __init__(self, section: Section = DefaultSection, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        global RegisteredSections
        if section not in RegisteredSections:
            RegisteredSections[section] = [self]
        else:
            RegisteredSections[section].append(self)


class Group(asyncclick.Group):
    command_class = Command


class HelpMessage:
    def render(self, project: Project, section: Sections):
        console = Global.console
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


@asyncclick.group(add_help_option=False, invoke_without_command=True, cls=Group)
@asyncclick.option('--remote', '-r', default='', help="Execute command in remote environment (ignored in native)")
@asyncclick.pass_context
def application(ctx: asyncclick.Context, remote: str):
    pass


@application.command(name='help', help="Display help message", section=DefaultSection)
def display_help_message():
    project = Unimake['project'].project
    Helper.render(project, RegisteredSections)


cmd = application.command
