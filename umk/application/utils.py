import functools
import os

import asyncclick


class State:
    Complete = "_UMK_COMPLETE" in os.environ
    Unsafe = "UMK_UNSAFE" in os.environ


class RemoteOption(asyncclick.Option):
    def __init__(self, *args, **kwargs):
        cls = None
        for arg in args:
            if issubclass(type(arg), asyncclick.Parameter):
                cls = arg
                break
        name = ("-R",)
        if cls:
            super(RemoteOption, self).__init__(name, cls=cls, **kwargs)
        else:
            super(RemoteOption, self).__init__(name, **kwargs)
        self.flag_value = "flag"
        self.is_flag = False
        self.help = "Execute in the default or specific remote environment"

    def handle_parse_result(self, ctx: asyncclick.Context, opts: dict[str, str], args: list[str]):
        r = opts.get('r')
        if issubclass(type(ctx.command), asyncclick.Group):
            if r in ctx.command.commands:
                args.append(r)
                opts['r'] = "___umk_option_remote___"
        return super(RemoteOption, self).handle_parse_result(ctx, opts, args)


class options:
    @staticmethod
    def remote(func):
        @asyncclick.option(cls=RemoteOption)
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


if not State.Complete:
    import sys

    from umk import core
    from umk import runtime


    # def forward(container: runtime.Container, default: bool, specific: str, cmd: list[str]):
        # if not default and not specific:
        #     return
        # rem: framework.remote.Interface = container.find_remote(default, specific)
        # # TODO Parse sys.argv and run it in the remote environment
        # print("Forwarding is not implemented !")
        # core.globals.close(0)


    def config(file: bool, presets: tuple[str] | None, overrides: None | tuple[str] = None) -> runtime.Options.Config:
        result = runtime.Options.Config()
        result.presets = list(presets)
        result.file = file
        if not overrides:
            return result
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
