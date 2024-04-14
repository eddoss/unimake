import os

import asyncclick
from asyncclick import Command

if not os.environ.get('_UMK_COMPLETE', None):
    import sys

    from umk import core
    from umk import framework
    from umk import runtime
    from umk.application.utils.printers import PropertiesPrinter


    def forward(container: runtime.Container, default: bool, specific: str, cmd: list[str]):
        if not default and not specific:
            return
        rem: framework.remote.Interface = container.find_remote(default, specific)
        # TODO Parse sys.argv and run it in the remote environment
        print("Forwarding is not implemented !")
        core.globals.close(0)


    def subcmd(name: str) -> list[str]:
        for i, arg in enumerate(sys.argv):
            if arg == name:
                return sys.argv[i:]


    def parse_config_overrides(raw: None | tuple[str] = None) -> dict[str, str]:
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
            asyncclick.Option(param_decls=["-C"], required=False, type=str, multiple=True, help="Config entry override"),
            asyncclick.Option(param_decls=["-P"], required=False, type=str, multiple=True, help="Config preset to apply"),
            asyncclick.Option(param_decls=["-F"], is_flag=True, help="Load config from file")
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
            asyncclick.Option(param_decls=["-C"], required=False, type=str, multiple=True, help="Config entry override"),
            asyncclick.Option(param_decls=["-P"], required=False, type=str, multiple=True, help="Config preset to apply"),
            asyncclick.Option(param_decls=["-F"], is_flag=True, help="Load config from file")
        ]
