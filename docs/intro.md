# Introduction

![diagram](diagrams/high-level-structure.svg)

# User project
User project is a regular project directory that layout as project of any language:
- Golang
- C/C++
- Rust (cargo)
- Python (poetry, pip)
- Empty (no codebase)
- ...

## .unimake
User project should contain `.unimake` folder which consists of the set of `.py` scripts that 
describes project maintenance, commandline interface, dependencies, etc. There are 2 required 
scripts:
- project.py
- cli.py

### .unimake/project.py
Contains instance of the class that was inherited from `umk.Project`. This instance **must** be named `project`.
```py
import umk 

project = umk.GoProject()
project.info.name.short = "project-name"
project.info.name.full = "Project Name"
project.info.version = "v1.0.0"
project.info.description = "Super puper mega description"
project.info.authors = [
    umk.Author('Author Name', 'author.name@email.com')
]
```
or 
```py
import umk 

class Project(umk.GoProject()):
    def __init__(self):
        self.info.name.short = "project-name"
        self.info.name.full = "Project Name"
        self.info.version = "v1.0.0"
        self.info.description = "Super puper mega description"
        self.info.authors = [
            umk.Author('Author Name', 'author.name@email.com')
        ]
        
project = Project()
```

### .unimake/cli.py
Contains project commandline interface. It's very easy to describe commands.
```py
from umk import cli
from project import project

@cli.cmd()
def build():
    project.build(...)

@cli.cmd(help="Run debug server (on port 2345 by default)")
@cli.opt('--port', type=int, default=2345)
def debug(port: int):
    project.debug(...)
```

# Commandline tools
Unimake provide commandline utilities named `umk` and `unimake` to call projects CLI and maintain any project aspects. 

## Tool: umk
The `umk` allows you to call any command from `.unimake/cli.py` in the specific, default or local environment. This 
tool consider the current working directory (see `pwd` command on unix) as a project that contains folder `.unimake`. 
That is all, the `umk` can do nothing else.

You need switch to project root directory and call any command from `.unimake/cli.py`:

```sh
cd my/project/root

umk help     # print default help message
umk build    # run build command
umk debug    # run debug command

...
```

## Tool: unimake
The `unimake` allows you to manage some part of the `.unimake` project and `Unimake Tool Set` itself:
- Initialize an empty directory as a project
- Manage remote environments
- Manage `unimake` and project extensions
- Etc
```sh
unimake --help
unimake version
unimake remote ...
unimake init ...
...
```

# Framework
Unimake framework is a python package named `umk`. You must use it when implements:
- `.unimake/project.py`
- `.unimake/cli.py`
- `.unimake/remotes.py`
- `.unimake/...`

This framework has convenient abstractions such as:
- project (basic, cmake, make, go, ...)
- version control system (git, svn, ...)
- system operations (filesystem, environs, shell, ...)
- adapters to commonly used utils (go, clangformat, ...)
- remote environments routines (docker, docker-compose, ssh)
- and more ...