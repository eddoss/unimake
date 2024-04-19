import functools

import asyncclick

import umk.core.globals
from umk import state


class options:
    @staticmethod
    def remote(func):
        # @asyncclick.option(cls=RemoteOption)
        @asyncclick.option("-R", is_flag=True, flag_value="___umk_flag___", help="Execute in the default or specific remote environment")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def style(func):
        @asyncclick.option("-s", default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    class config:
        @staticmethod
        def all(func):
            @asyncclick.option("-F", is_flag=True, help="Load config from file")
            @asyncclick.option("-P", required=False, type=str, multiple=True, help="Config preset to apply")
            @asyncclick.option("-C", required=False, type=str, multiple=True, help="Config entry override")
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        @staticmethod
        def entry(func):
            @asyncclick.option("-C", required=False, type=str, multiple=True, help="Config entry override")
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        @staticmethod
        def preset(func):
            @asyncclick.option("-P", required=False, type=str, multiple=True, help="Config preset to apply")
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        @staticmethod
        def file(func):
            @asyncclick.option("-F", is_flag=True, help="Load config from file")
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper


if not state.complete:
    import sys

    from umk import core
    from umk import runtime


    def forward(container: runtime.Container):
        if state.remote.default:
            re = container.find_remote(state.remote.default, "")
        elif state.remote.specific.strip():
            re = container.find_remote(False, state.remote.specific)
        else:
            return
        umk.core.globals.console.print(f"[bold]Forward execution to '{re.name}' remote environment: '{' '.join(state.remote.cmd)}'")
        re.execute(state.remote.cmd)
        sys.exit(0)

    def config(file: bool, presets: tuple[str] | None = None, overrides: None | tuple[str] = None) -> runtime.Options.Config:
        result = runtime.Options.Config()
        result.presets = list(presets) if presets else []
        result.file = file
        if not overrides:
            return result
        if overrides is not None:
            for entry in overrides:
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
                result.overrides[name] = value
        return result
