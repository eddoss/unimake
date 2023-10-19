# Unimake
`unimake` is a set of development tools and frameworks for project maintaining. This tools makes it easy to organize development routines (such as building, testing, linting, running, etc) for a specific code base. 
## Features
- Convenient framework for a project description
- Python is the only language for everything
- Debuggable pipeline (unlike regular shell scripts)
- Easiest way to create a powerful CLI (like `make` but more flexible)
- Adapters for a commonly used build systems (`go`, `cmake`, ...)
- Run project targets in remote environment (dev-container, remote server, etc)
# How it works ?
Unimake provides the command line utility `umk` and the framework `umk` in Python.

A specific project must contain at least 2 scripts:
- `.unimake/project.py` - project info, build steps, etc.
- `.unimake/cli.py` - command line interface to interact with project

`umk` tool allows you to execute a command from `.unimake/cli.py`
### Script project.py

```py
import umk 

class Project(umk.GoProject):  
    def __init__(self):  
        super().__init__()  
        self.git = umk.git()
        self.info.name.short = "project-name"
        self.info.name.full = "Project Name"
        self.info.version = umk.tag(self.git, "v1.0.0")
        self.info.authors = [
            umk.Author('Author Name', 'author.name@email.com')
        ]
        self.info.description = "Super puper mega description"  
        self.go = umk.Go.find("1.19")
        self.dlv = umk.Delve.find()
  
    async def build(self, mode: str):
        args = umk.GoBuildArgs.new(mode)  
        args.output = self.layout.output / 'foo'
        args.sources.append(self.layout.cmd / 'foo')
        args.flags.go.append('-mod=vendor')
        await self.go.build(args).asyn()
  
    def vendor(self):
        self.go.mod.tidy().sync()
        self.go.mod.vendor().sync()
  
    def debug(self, port=2345):
        self.dlv.exec(
            binary=self.layout.output / 'foo',
            flags=umk.DelveFlags(port)
        ).sync()
  
project = Project()
```
### Script cli.py

```py
from umk import cli  
from project import project  

@cli.cmd()
def vendor():  
    project.vendor()

@cli.cmd()
@cli.opt('--mode', default='debug', help='Build mode (debug|release)')
async def build(mode: str):
    await project.build(mode)

@cli.cmd(help="Run debug server (on port 2345 by default)")
@cli.opt('--port', type=int, default=2345)  
def debug(port: int):  
    project.debug(port)
```
### Execute projects command
```sh
cd path/to/project/root
umk vendor
umk build
umk debug --port 3000
``` 
# Build requirements
- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Make](https://www.gnu.org/software/make/manual/make.html)
# Build and install
```sh
make dependencies
make build
sudo cp ./dist/umk /usr/bin/umk
```