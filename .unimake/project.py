import os
import shutil

from config import Config
from umk.kit import project, system, target
from umk import console


class Layout(project.Layout):
    @property
    def dist(self):
        return self.root / "dist"

    @property
    def development(self):
        return self.root / "development"

    @property
    def docs(self):
        return self.root / "docs"

    @property
    def tests(self):
        return self.root / "tests"

    @property
    def umk(self):
        return self.root / "deployment"

    @property
    def venv(self):
        return self.root / ".venv"


@project.custom
class Project(project.Scratch):
    def __init__(self):
        super().__init__()
        self.layout = Layout()
        self.info.id = "umk"
        self.info.name = "Unimake"
        self.info.version = "v0.1.3"
        self.info.description = (
            "Unimake is a set of development tools and frameworks for project maintaining. "
            "This tools makes it easy to organize development routines (such as building, "
            "testing, linting, running, etc) for a specific code base."
        )

    def poetry(self, *args: str):
        sh = system.Shell()
        sh.name = "poetry"
        sh.cmd = ["poetry"] + list(args)
        sh.workdir = self.layout.root
        sh.log = True
        sh.sync()

    def pip(self, *args: str):
        sh = system.Shell()
        sh.name = "pip"
        sh.cmd = ["pip"] + list(args)
        sh.workdir = self.layout.root
        sh.log = True
        sh.sync()


@target.function(name="clean", description="Clean project")
def _(_, p: Project):
    system.Shell(
        cmd=[
            "find",
            ".",
            "-type",
            "f",
            "-name",
            '"*.py[co]"',
            "-delete",
            "-or",
            "-type",
            "d",
            "-name",
            '"__pycache__"',
            "-delete",
        ],
    ).sync()
    shutil.rmtree(p.layout.dist, ignore_errors=True)


@target.function(name="build", description="Build python package")
def _(_, p: Project):
    p.poetry("build")


@target.function(name="install", description="Install package")
def _(_, p: Project):
    pkg = p.layout.dist.as_posix() + f"/{p.info.id}-{p.info.version[1:]}-py3-none-any.whl"
    p.pip("uninstall", "--yes", "umk")
    p.pip("install", pkg)


@target.function(name="dependencies", description="Install project dependencies")
def _(_, p: Project):
    p.poetry("install")


@target.function(name="dependencies.dev", description="Install development dependencies")
def _(_, p: Project):
    p.poetry("install", "--with=dev")


@target.function(name="env.up", description="Create .venv")
def _(_, c: Config, p: Project):
    p.poetry("env", "use", "-n", "--", system.which(c.py))


@target.function(name="env.down", description="Destroy .venv")
def _(_, p: Project):
    shutil.rmtree(p.layout.venv, ignore_errors=True)


@target.function(name="docs", label="docs", description="Generate documentation")
def _(p: Project):
    commands = {
        # "inspect": ["umk", "inspect"],
        # "config-inspect": ["umk", "config", "inspect"],
        # "config-inspect-preset": ["umk", "config", "inspect", "-P", "local"],
        # "config-inspect-override": ["umk", "config", "inspect", "-C", "usermod=no", "-C", "debug.port=7777"],

        "target-inspect-server-debug": ["umk", "target", "inspect", "server"],
        "target-inspect-server-release": ["umk", "target", "inspect", "server.release"],
    }

    config = p.layout.development / "freeze.json"
    sample = p.layout.docs / "sample"
    output = p.layout.docs / "screens"

    if not output.exists():
        os.makedirs(output)

    for name, cmd in commands.items():
        console.print(f"Run {name} {cmd}")
        exe = f'"{" ".join(cmd)}"'
        out = output / f"sample-{name}.png"
        sh = system.Shell()
        sh.name = "freeze"
        sh.cmd = ["freeze", "-c", config, "-x", exe, "-o", out]
        sh.workdir = sample
        sh.sync(log=True)
