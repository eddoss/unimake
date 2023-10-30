import dotenv
import sys
from pathlib import Path
from importlib import util as importer
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
