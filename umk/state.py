import os
import sys


class RemoteState:
    def __init__(self, completion: bool):
        self.default: bool = False
        self.specific: str = ""
        self.cmd = []

        if completion:
            return

        if len(sys.argv) < 1:
            return

        commands = {
            "run": True,
            "release": True,
            "config": False,
            "inspect": False,
            "format": False,
            "remote": False,
            "target": False,
        }

        position = None
        for i, arg in enumerate(sys.argv[1:]):
            if arg in commands:
                return
            if arg.startswith("-R="):
                self.specific = arg.lstrip("-R=")
                position = i
                break
            elif arg == "-R":
                self.default = True
                position = i
                break

        if position is None:
            return

        subcmd = ""
        allowed = False
        for arg in sys.argv[1:]:
            if arg in commands:
                subcmd = arg
                allowed = commands.get(arg)
                break
        if not subcmd:
            self.default = False
            self.specific = ""
            return

        if not allowed:
            print(f"Subcommand '{subcmd}' is not remotable !", file=sys.stderr)
            sys.exit(-1)
        else:
            sys.argv.pop(position + 1)
            self.cmd = ["umk"] + sys.argv[1:]


complete: bool = "_UMK_COMPLETE" in os.environ
unsafe: bool = "UMK_UNSAFE" in os.environ
remote = RemoteState(complete)
