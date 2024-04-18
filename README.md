![Deploy PyPi](https://github.com/eddoss/unimake/actions/workflows/publish.yml/badge.svg)

# Unimake
`unimake` is a set of development tools and frameworks for project maintaining. This tools makes it easy to organize development routines (such as building, testing, linting, running, etc) for a specific code base.

## Goals
- Allow gophers to use the full power of Python instead of makefiles and shell scripts.
- Facilitate the task of product building consisting of several projects in different languages.
- Provide the opportunity to develop debuggable project maintenance scripts.
- Automate project maintenance routines.

## Features
- Convenient framework for a project description
- Python is the only language for everything
- Debuggable pipeline (unlike regular shell scripts)
- Easiest way to create a powerful CLI (like `make` but more flexible)
- Adapters for a commonly used build systems (`go`, `cmake`, ...)
- Run project targets in remote environment (dev-container, remote server, etc)

# How it works ?
Unimake provides the Python framework (`umk`) and project commandline tool (`umk`).

A specific project must contain at least 1 module:
- `.unimake/project.py` - project info, target descriptions and release function
Other modules are optionals:
- `.unimake/config.py` - contains project config class and config presets
- `.unimake/remotes.py` - contains remote environments to run targets in

![how-unimake-works](docs/diagrams/high-level.svg)
## Sample project
Sources are [here](docs/sample).
### Project and targets
```py
# File      .unimake/config.py
# Optional  no

from umk.kit import project, target
from config import Config


@project.golang
def _(s: project.Golang):
    s.info.id = "sample"
    s.info.name = "Sample Project"
    s.info.description = "Sample project detailed description"
    s.info.version = "v0.2.0"
    s.info.contrib("John Doe", "john.doe@mail.com")


@target.go.binary
def _(s: target.GolangBinary, c: Config, p: project.Golang):
    s.name = "server"
    s.label = "Server"
    s.description = "Server application"
    s.tool = p.tool
    s.build.output = p.layout.root / "server"
    s.build.source = [p.layout.cmd / "server"]
    s.debug.port = c.debug.port  # Read server debug port from config


@target.go.mod
def _(s: target.GolangMod, _, p: project.Golang):
    s.name = "dependencies.go"
    s.label = "Golang Dependencies"
    s.description = "List of golang packages required to build project"
    s.tool = p.tool
    s.path = p.layout.root


@target.packages
def _(s: target.SystemPackages):
    s.name = "dependencies.os"
    s.label = "System Package Dependencies"
    s.description = "List of system packages required to build project"
    s.apt_get.sudo = True
    s.apt_get.items = ["golang"]


@project.releaser
def _(c: Config):
    target.run("dependencies.os")
    target.run("dependencies.go")
    if c.debug.on:
        target.run("server")
    else:
        target.run("server")
```
### Config
```py
# File      .unimake/config.py
# Optional  yes 

from umk import core
from umk.kit import config


@config.register
class Config(config.Interface):
    class Debug(core.Model):
        on: bool = core.Field(False, description="Enable debug info")
        port: int = core.Field(default=2345, description="Port to start debugger on")
    debug: Debug = core.Field(default_factory=Debug)
    usermod: bool = core.Field(True, description="Create user inside development container")


@config.preset(name="local")
def _(c: Config):
    c.debug.port = 2020
```
### Development environment
```py
# File      .unimake/remote.py
# Optional  yes

from umk.kit import remote, project, system
from umk.kit.adapter import docker
from config import Config


@remote.docker.compose
def _(s: remote.DockerCompose, c: Config, p: project.Golang):
    s.name = "dev"
    s.description = "Project development container"
    s.default = True

    u = system.user()

    # Dockerfile
    f = docker.File(path=p.layout.root, name="dev.dockerfile")
    f.froms("ubuntu")
    if c.usermod:
        f.run([
            f"apt-get update",
            f"apt-get -y install sudo",
            f"mkdir -p /etc/sudoers.d",
            f'echo "{u.name} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
            f"groupadd -g {u.group.id} {u.name}",
            f"useradd -m -u {u.id} -d /home/{u.name} -g {u.group.id} -s /bin/sh {u.name}",
        ])
        f.user(u.id)
        f.env("PATH", f"$PATH:/home/{u.name}/.local/bin")
        f.run([f"sudo chown {u.name}:{u.name} /home/{u.name}"])
        f.run([
            "sudo apt-get -y install git",
            "sudo apt-get -y install python3",
            "sudo apt-get -y install pip",
        ])
    else:
        f.run([
            "apt-get -y install git",
            "apt-get -y install python3",
            "apt-get -y install pip",
        ])
    f.run(["pip install umk"])

    # Compose service
    b = docker.ComposeService()
    b.build = docker.ComposeBuild()
    b.build.context = f.path
    b.build.dockerfile = f.name
    b.image = "project-image"
    b.container_name = "dev"
    b.ports = ["2233:2233"]
    b.hostname = "dev"
    b.working_dir = "/workdir"
    if c.usermod:
        b.user = f"{u.id}:{u.group.id}"
        b.working_dir = f"/home/{u.name}/workdir"
    b.volumes.bind(src=p.layout.root, dst=b.working_dir)
    b.entrypoint = ["sleep", "infinity"]

    s.dockerfiles.append(f)
    s.composefile.services["dev"] = b
    s.composefile.path = p.layout.root
    s.service = "dev"
```