import typing as t

import beartype

beartype.BeartypeConf.is_color = False

import asyncio
import dotenv
import sys
import asyncclick

from asyncclick import argument as arg
from asyncclick import option as opt
from pathlib import Path
from importlib import util as importer
from beartype import beartype
from beartype.typing import Optional
from rich.table import Table
from rich.syntax import Syntax
from umk.globals import Global
from umk.project import Project


class DotUnimake:
    def __init__(self, root: Path):
        sys.path.insert(0, root.as_posix())
        self._root = root
        self._modules = {}

    def __getitem__(self, module_name: str):
        return self._modules[module_name]

    def validate(self):
        console = Global.console
        if not self._root.exists():
            if Global.completion:
                sys.exit()
            console.print("[bold yellow]Unimake warning !")
            console.print("[bold yellow]"
                          "Current directory is not a Unimake project. "
                          "Unimake project must contain '.unimake' directory with 'project.py' script. "
                          "If you need to create a project get initialization help at first and after "
                          "setup a '.unimake'")

            table = Table(show_header=False, show_edge=True, show_lines=False)
            table.add_column("", justify="left", style="green bold", no_wrap=True)
            table.add_column("", justify="left", style="green", no_wrap=True)
            table.add_row('$ unimake init --help', 'Get initialization details')
            table.add_row('$ unimake init ...', 'Initialize a project')

            console.print(table)
            sys.exit()

        if not self._root.is_dir():
            if Global.completion:
                sys.exit()
            console.print(f"[bold bold red]Unimake error !")
            console.print(f"[bold red]Found '.unimake' but it's not a folder. "
                          f"Try to remove '.unimake' at first and init a project.")

            table = Table(show_header=False, show_edge=True, show_lines=False)
            table.add_column("", justify="left", style="green bold", no_wrap=True)
            table.add_column("", justify="left", style="green", no_wrap=True)
            table.add_row('$ unimake init --help', 'Get initialization details')
            table.add_row('$ unimake init ...', 'Initialize a project')

            console.print(table)
            sys.exit()

    def load_dotenv(self):
        file = self._root / '.env'
        if not file.exists():
            return
        try:
            dotenv.load_dotenv(file)
        except Exception as e:
            Global.console.print(str(e))
            sys.exit()

    def load_cli(self):
        self.script('cli')
        # sections = unimake['cli'].umk.application.main.sections
        # for o in unimake['cli'].__dict__.values():
        #     if issubclass(type(o), asyncclick.Command):
        #         if o.name == 'help':
        #             continue
        #         application.add_command(o, o.name)

    def load_project(self):
        self.script('project')
        module = self['project']
        if not hasattr(module, 'project') or not issubclass(type(module.project), Project):
            code = """
            import umk

            project = umk.Project() # or umk.GoProject, umk.CMakeProject, etc
            project.info.name.short = 'super-project'
            project.info.name.full = 'Super mega project'
            project.info.description = 'Super project description'
            """
            Global.console.print("[bold red]Unimake error: instance of the 'umk.Project' was not found !")
            Global.console.print(
                "[bold red]File [underline]'.unimake/project.py'[/underline] must contains instance of the Project")
            Global.console.print(Syntax(code, "python", theme='monokai', line_numbers=False))

    def script(self, name: str):
        if name in self._modules:
            print(f'ExternalModules.load: module "{name}" already exists', file=sys.stderr)
            sys.exit(-1)
        try:
            file = self._root / f'{name}.py'
            spec = importer.spec_from_file_location(name, file)
            module = importer.module_from_spec(spec)
            sys.modules[f'umk:{name}'] = module
            spec.loader.exec_module(module)
            self._modules[name] = module
        except Exception:
            Global.console.print_exception(show_locals=False, max_frames=1)


class Section:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @beartype
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    @beartype
    def description(self, value: str):
        self._description = value

    @beartype
    def __init__(self, name: str, description: str = ''):
        self._name = name
        self._description = description

    def __hash__(self):
        return hash((self._name, self._description))


Sections = dict[Section, list[asyncclick.Command]]


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


unimake: Optional[DotUnimake] = None
help_message = HelpMessage()
default_section = Section(name='Default', description='Default commands')
registered_sections: Sections = {default_section: []}


class Command(asyncclick.Command):
    def __init__(self, section: Section = default_section, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        global registered_sections
        if section not in registered_sections:
            registered_sections[section] = [self]
        else:
            registered_sections[section].append(self)


class Group(asyncclick.Group):
    command_class = Command


@asyncclick.group(add_help_option=False, invoke_without_command=True, cls=Group)
@asyncclick.option('--remote', '-r', default='', help="Execute command in remote environment (ignored in native)")
@asyncclick.pass_context
def application(ctx: asyncclick.Context, remote: str):
    pass


@application.command(name='help', help="Display help message", section=default_section)
def display_help_message():
    project = unimake['project'].project
    help_message.render(project, registered_sections)


cmd = application.command


@beartype
def sec(section: Section = default_section):
    def proxy(command):
        global registered_sections
        if section not in registered_sections:
            registered_sections[section] = [command]
        else:
            registered_sections[section].append(command)
        return command
    return proxy