import os

import asyncclick

from umk.application.cmd import root
from umk.application import utils

if not os.environ.get('_UMK_COMPLETE', None):
    from rich.table import Table
    from umk import runtime
    from umk import core
    from umk.framework.remote.interface import Interface


@root.group(help="Remote environments management commands",)
@asyncclick.option('-n', default="", help="Remote environment name")
@utils.options.config.all
@asyncclick.pass_context
async def remote(ctx: asyncclick.Context, n: str, c: tuple[str], p: tuple[str], f: bool):
    pass
    opt = runtime.Options()
    opt.config = utils.config(f, p, c)
    runtime.c.load(opt)

    if ctx.invoked_subcommand != "ls":
        ctx.ensure_object(dict)
        ctx.obj["instance"] = runtime.c.find_remote(n == "", n)


@remote.command(help="Build remote environment")
@asyncclick.pass_context
def build(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.build()


@remote.command(help="Destroy remote environment")
@asyncclick.pass_context
def destroy(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.destroy()


@remote.command(help="Start remote environment")
@asyncclick.pass_context
def up(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.up()


@remote.command(help="Stop remote environment")
@asyncclick.pass_context
def down(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.down()


@remote.command(help="Login remote environment")
@asyncclick.pass_context
def login(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.login()


@remote.command(help="Open remote environment shell")
@asyncclick.pass_context
def shell(ctx: asyncclick.Context):
    instance: Interface = ctx.obj.get("instance")
    instance.shell()


@remote.command(help='List project remote environments')
def ls():
    table = Table(show_header=True, show_edge=True, show_lines=False)
    table.add_column("Name", justify="left", style="", no_wrap=True)
    table.add_column("Default", justify="center", style="", no_wrap=True)
    table.add_column("Description", justify="left", style="", no_wrap=True)
    for rem in runtime.c.remotes:
        default = ''
        if rem.default:
            default = 'x'
            table.add_row(f"{rem.name}", default, rem.description, style="yellow bold")
        else:
            table.add_row(rem.name, default, rem.description)
    core.globals.console.print(table)
    core.globals.close()


@remote.command(name='exec', help="Execute command in remote environment")
@asyncclick.argument('program', required=True, nargs=1)
@asyncclick.argument('arguments', required=False, nargs=-1)
@asyncclick.pass_context
def execute(ctx: asyncclick.Context, program: str, arguments: tuple[str]):
    cmd = list(arguments)
    cmd.insert(0, program)
    rem: Interface = ctx.obj.get("instance")
    rem.execute(cmd=cmd)


@remote.command(help='Show remote environment details')
@utils.options.style
@asyncclick.pass_context
def inspect(ctx: asyncclick.Context, s: str):
    details: core.Object = ctx.obj.get("instance").object()
    if s == "style" or s == "":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="", no_wrap=True)
        table.add_column("Description", justify="left", style="", no_wrap=True)
        table.add_column("Value", justify="left", style="", no_wrap=True)
        for prop in details.properties:
            table.add_row(prop.name, prop.description, str(prop.value))
        core.globals.console.print(table)
    elif s == "json":
        core.globals.console.print_json(core.json.text(details))


@remote.command(help="Upload files to remote environment")
@asyncclick.argument('items', required=False, nargs=-1)
@asyncclick.pass_context
def upload(ctx: asyncclick.Context, items: tuple[str]):
    rem: Interface = ctx.obj.get("instance")
    paths = split(items)
    if not paths:
        return
    rem.upload(paths)


@remote.command(help="Download files from remote environment")
@asyncclick.argument('items', required=False, nargs=-1)
@asyncclick.pass_context
def download(ctx: asyncclick.Context, items: tuple[str]):
    rem: Interface = ctx.obj.get("instance")
    paths = split(items)
    if not paths:
        return
    rem.download(paths)


def split(items: tuple[str]) -> dict[str, str]:
    def error():
        core.globals.console.print("[bold red]Invalid upload/download item!")
        core.globals.console.print("[bold red]Pattern")
        core.globals.console.print("[bold red]    upload:   <local/file>:<remote/file>")
        core.globals.console.print("[bold red]    download: <remote/file>:<local/file>")
    result = {}
    for item in items:
        if ':' not in item:
            error()
            return {}
        s = item.split(':')
        result[s[0]] = s[1]
    return result
