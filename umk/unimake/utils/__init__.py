import os

import asyncclick
from asyncclick import Command

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    import sys

    from umk import core
    from umk import framework
    from umk.unimake.utils.printers import PropertiesPrinter


def find_remote(default: bool, specific: str) -> 'framework.remote.Interface':
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


class ConfigableCommand(asyncclick.Command):
    def __init__(
        self,
        name: None | str,
        context_settings=None,
        callback=None,
        params: None | list[asyncclick.Parameter] = None,
        help: None | str = None,
        epilog: None | str = None,
        short_help: None | str = None,
        options_metavar: None | str = "[OPTIONS]",
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False
    ) -> None:
        super().__init__(name, context_settings, callback, params, help, epilog, short_help, options_metavar, add_help_option, no_args_is_help, hidden, deprecated)
        self.params += [
            asyncclick.Option(param_decls=["-c"], required=False, type=str, multiple=True, help="Config entry override"),
            asyncclick.Option(param_decls=["-p"], required=False, type=str, help="Config preset to apply")
        ]


class ConfigableGroup(asyncclick.Group):
    def __init__(
        self,
        name: None | str = None,
        commands: None | dict[str, Command] | list[Command] = None,
        **attrs
    ) -> None:
        super().__init__(name, commands, **attrs)
        self.params += [
            asyncclick.Option(param_decls=["-c"], required=False, type=str, multiple=True, help="Config entry override"),
            asyncclick.Option(param_decls=["-p"], required=False, type=str, help="Config preset to apply"),
            asyncclick.Option(param_decls=["-f"], is_flag=True, help="Load config from file")
        ]


def parse_config_overrides(raw: None | list[str] = None) -> dict[str, str]:
    if not raw:
        return {}
    result = {}
    for entry in raw:
        name = ""
        i = 0
        for i, sym in enumerate(entry):
            if sym != "=":
                name += sym
            # TODO Validate entry symbols
            else:
                break
            if i > len(entry):
                # TODO Invalid syntax
                print(f"Invalid config entry: {entry}", file=sys.stderr)
                core.globals.close(-1)
        value = entry[i+1:]
        result[name] = value
    return result
