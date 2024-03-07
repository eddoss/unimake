import sys


class Field:
    def __init__(self):
        self.flags: list[str] = []
        self.flag: str = ""
        self.name = ""
        self.type: str = ""
        self.doc: str = ""
        self.default = None
        self.factory = None

    def __str__(self):
        cli = ""
        if self.type == "None | int":
            cli = f'kit.cli.Int(name="{self.flag}")'
        elif self.type == "None | bool":
            cli = f'kit.cli.Bool(name="{self.flag}")'
        elif self.type == "None | str":
            cli = f'kit.cli.Str(name="{self.flag}")'
        elif self.type.startswith("list"):
            cli = f'kit.cli.List(name="{self.flag}")'
        elif self.type.startswith("dict"):
            cli = f'kit.cli.Dict(name="{self.flag}")'
        else:
            cli = f'kit.cli.Obj(name="{self.flag}")'
            self.factory = self.type
            self.default = None

        if self.default:
            return f'{self.name}: {self.type} = core.Field(\n    default={self.default},\n    cli={cli},\n    description="{self.doc}"\n)'
        elif self.factory:
            return f'{self.name}: {self.type} = core.Field(\n    default_factory={self.factory},\n    cli={cli},\n    description="{self.doc}"\n)'
        else:
            print("INVALID FIELD !", file=sys.stderr)
            print(f"name={self.name} flags={self.flags} type={self.type} default={self.default} factory={self.factory} doc={self.doc}", file=sys.stderr)

    def update(self):
        self.doc = self.doc.strip().replace('"', "'")
        for flag in self.flags:
            self.flag = flag
            if flag.startswith("--"):
                break
        self.name = self.flag[2:].replace("-", "_")
        if not self.name and self.flags:
            self.name = self.flags[0][1:].replace("-", "_")
        if self.type == "strings":
            self.type = "list[str]"
            self.factory = "list"
        if self.type == "list":
            self.type = "list[str]"
            self.factory = "list"
        if self.type in ("ulimit", "mount"):
            self.type = "list"
            self.factory = "list"
        elif self.type == "stringArray":
            self.type = "dict[str, str]"
            self.factory = "dict"
        elif self.type == "filter":
            self.type = "dict[str, str]"
            self.factory = "dict"
        elif self.type == "string":
            self.type = "None | str"
            self.default = "None"
        elif self.type in ("bytes", "uint16", "int", "decimal", "duration"):
            self.type = "None | int"
            self.default = "None"
        elif not self.type.strip():
            self.type = "None | bool"
            self.default = "None"


def parse_opts(text: str):
    text = text.strip()
    if not text:
        return
    for line in text.split("\n"):
        line = line.strip()
        field = Field()
        chunks = line.split()
        for chunk in chunks:
            if chunk.startswith("--"):
                field.flags.append(chunk)
            elif chunk.startswith("-"):
                if chunk.endswith(","):
                    chunk = chunk.rstrip(",")
                field.flags.append(chunk)
            elif not field.type:
                if not field.doc and not chunk.istitle():
                    field.type = chunk
                else:
                    field.doc += chunk + " "
            else:
                field.doc += chunk + " "
        field.update()
        print(field)


def parse_cmds(text: str):
    text = text.strip()
    if not text:
        return
    for line in text.split("\n"):
        line = line.strip()
        chunks = line.split()
        cmd = chunks[0]
        des = "".join(chunks[1:])
        print(
            f"\ndef {cmd}(self):\n"
            f"    pass"
        )

parse_opts(
"""
      --blkio-weight uint16        Block IO (relative weight), between 10 and 1000, or 0 to disable (default 0)
      --cpu-period int             Limit CPU CFS (Completely Fair Scheduler) period
      --cpu-quota int              Limit CPU CFS (Completely Fair Scheduler) quota
      --cpu-rt-period int          Limit the CPU real-time period in microseconds
      --cpu-rt-runtime int         Limit the CPU real-time runtime in microseconds
  -c, --cpu-shares int             CPU shares (relative weight)
      --cpus decimal               Number of CPUs
      --cpuset-cpus string         CPUs in which to allow execution (0-3, 0,1)
      --cpuset-mems string         MEMs in which to allow execution (0-3, 0,1)
  -m, --memory bytes               Memory limit
      --memory-reservation bytes   Memory soft limit
      --memory-swap bytes          Swap limit equal to memory plus swap: -1 to enable unlimited swap
      --pids-limit int             Tune container pids limit (set -1 for unlimited)
      --restart string             Restart policy to apply when a container exits
"""
)

parse_cmds(
"""

"""
)
