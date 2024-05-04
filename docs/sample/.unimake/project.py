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
def _(s: target.GolangMod, p: project.Golang):
    s.name = "deps.go"
    s.label = "Golang Dependencies"
    s.description = "List of golang packages required to build project"
    s.tool = p.tool
    s.path = p.layout.root


@target.packages
def _(s: target.SystemPackages):
    s.name = "deps.os"
    s.label = "System Package Dependencies"
    s.description = "List of system packages required to build project"
    s.apt_get.sudo = True
    s.apt_get.items = ["golang"]


@project.releaser
def _(c: Config):
    target.run("deps.os")
    target.run("deps.go")
    if c.debug.on:
        target.run("server")
    else:
        target.run("server.release")
