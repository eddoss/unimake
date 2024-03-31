import sys

from umk import core
from umk import framework


def find_remote(default: bool, specific: str) -> framework.remote.Interface:
    result = framework.remote.find("" if default else specific)
    if default and not result:
        core.globals.error_console.print(
            'Failed to find default remote environment! '
            'Please specify it in the .unimake/remotes.py'
        )
        core.globals.close(-1)
    elif not result and specific:
        core.globals.console.print(
            f"Failed to find remote environment '{specific}'! "
            f"Please create it in the .unimake/remotes.py"
        )
        core.globals.close(-1)
    return result


def subcmd(name: str) -> list[str]:
    for i, arg in enumerate(sys.argv):
        if arg == name:
            return sys.argv[i:]
