![diagram](diagrams/high-level.svg)

# User project
User project is a regular project directory that layout as project of any language:
- Golang
- C/C++
- Rust
- Python
- ...

## .unimake
User project should contain `.unimake` folder which consists of the set of `.py` scripts that 
describes project maintenance, commandline interface, dependencies, etc. There are 2 required 
scripts:
- project.py
- cli.py

### .unimake/project.py
Contains instance of the class that was inherited from `umk.Project`. This instance should be named `project`.
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

### .unimake/cli.py
Contains project commandline interface. It's very easy to describe commands.
```py
from umk import cli
from project import project

@cli.cmd()
def build():
    # run project.build(...)
    pass

@cli.cmd(help="Run debug server (on port 2345 by default)")
@cli.opt('--port', type=int, default=2345)
def debug(port: int):
    # run debug
    pass
```

## Unimake CLI
Unimake provide commandline tool named `umk` to manage projects CLI. This tool consider the current working directory
(see `pwd` command on unix) as a project that contains `.unimake` folder. 

### Command layers
This tool has 2 layers of the commands:
- native 
- external

#### Native commands layer
These commands relate to the `umk` tool itself, such commands starts with `/`:
```sh
umk /version
umk /help
umk /init
...
```

#### External commands layer
These commands relate to the `.unimake` project, such commands should not start with `/` !
The list of external commands consists of what is described in the `.unimake/cli.py` script. Inorder to list external
commands go to project root and run:
```
umk help
```
The `umk help` is an auto-generated command. 

## Unimake framework
Unimake framework is a python package named `umk`. You must use it when implements:
- `.unimake/project.py`
- `.unimake/cli.py`

This framework has convenient abstractions such as:
- project (basic, cmake, make, go, ...)
- version control system (git, svn, ...)
- system operations (filesystem, environs, shell, ...)
- adapters to commonly used utils (go, clangformat, ...)
- and more ...