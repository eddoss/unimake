# Tool: umk

## Description
This tool allows you to call any command from `.unimake/cli.py`. `umk` works only in the directories that contains 
`.unimake`, if you run it outside you will get an error message !

## Features
- Call command in the **local** environment
- Call command in the **default** remote environment
- Call command in the **specific** remote environment

## How to use ?
Let's look at an example of a `.unimake` folder:
```sh
workdir
└──.unimake
    ├── cli.py
    └── remotes.py
```

```python
# cli.py 

from umk import cli

@cli.cmd()
def foo(): ...

@cli.cmd()
def bar(): ...
```
The `cli.py` contains just two command `foo` and `bar`, this command has no descriptions, options, arguments or 
something else. You can call this commands by `umk`.

```python
# remotes.py 

from umk.framework import remote


@remote.register
def development():
    return remote.DockerContainer(name="dev", container='app-dev', default=True)


@remote.register
def production():
    return remote.DockerContainer(name="prod", container='app')
```
The `remotes.py` contains two remote environments where you can execute command:
- **production** - abstract production docker container
- **development** - abstract development docker container

| How to                                               | Command                   | Example         |
|:-----------------------------------------------------|:--------------------------|:----------------|
| Run in the **local** environment (host/shell)        | umk [COMMAND]             | umk foo         |
| Run in the **default** remote environment            | umk -r [COMMAND]          | umk -r bar      |
| Run in the **specific** remote environment           | umk -r [REMOTE] [COMMAND] | umk -r prod bar |
| Show help message                                    | umk help                  | umk help        |

**NOTE: Do not forget to switch to project root !**  

## Execution flow
At first of all `umk` check whether `${PWD}/.unimake` exists and this structure is ok. It will show an error message,
if something wrong. If you try to call in the remote environment, but it is not exists `umk` will error.

![umk-exec-flow.svg](diagrams/umk-exec-flow.svg)

