import os

import asyncclick as click
from asyncclick import Context

from umk.tools.unimake import application
from umk.tools import utils

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core


@application.group(cls=utils.ConfigableGroup, help="Remote environments management commands",)
@click.option('--name', '-n', default="", help="Remote environment name")
@click.pass_context
async def remote(ctx: click.Context, name: str, c: list[str], p: str):
    lo = runtime.LoadingOptions(root=core.globals.paths.unimake)
    lo.config.overrides = utils.parse_config_overrides(c)
    lo.config.presets = [p] if p else []
    lo.modules.project = runtime.OPT
    lo.modules.config = runtime.OPT
    lo.modules.remotes = runtime.YES
    runtime.load(lo)

    ctx.ensure_object(dict)
    ctx.obj["instance"] = utils.find_remote(name == "", name)


@remote.command(help="Build remote environment")
@click.pass_context
def build(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.build()


@remote.command(help="Destroy remote environment")
@click.pass_context
def destroy(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.destroy()


@remote.command(help="Start remote environment")
@click.pass_context
def up(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.up()


@remote.command(help="Stop remote environment")
@click.pass_context
def down(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.down()


@remote.command(help="Open remote environment shell")
@click.pass_context
def shell(ctx: click.Context):
    instance = ctx.obj.get("instance")
    instance.shell()


@remote.command(help='List project remote environments')
def ls():
    table = Table(show_header=True, show_edge=True, show_lines=False)
    table.add_column("Name", justify="left", style="", no_wrap=True)
    table.add_column("Default", justify="center", style="", no_wrap=True)
    table.add_column("Description", justify="left", style="", no_wrap=True)
    for rem in framework.remote.iterate():
        default = ''
        if rem.default:
            default = 'x'
            table.add_row(f"{rem.name}", default, rem.description, style="yellow bold")
        else:
            table.add_row(rem.name, default, rem.description)
    core.globals.console.print(table)
    core.globals.close()


@remote.command(name='exec', help="Execute command in remote environment")
@click.argument('program', required=True, nargs=1)
@click.argument('arguments', required=False, nargs=-1)
@click.pass_context
def execute(ctx: click.Context, program: str, arguments: tuple[str]):
    cmd = list(arguments)
    cmd.insert(0, program)
    rem: framework.remote.Interface = ctx.obj.get("instance")
    rem.execute(cmd=cmd)


@remote.command(help='Show remote environment details')
@click.option('--format', '-f', default="table", type=click.Choice(["table", "json", "yaml"], case_sensitive=False), help="Output format")
@click.pass_context
def inspect(ctx: Context, format: str):
    rem: framework.remote.Interface = ctx.obj.get("instance")
    if format == "table" or format == "":
        table = Table(show_header=True, show_edge=True, show_lines=True)
        table.add_column("Name", justify="left", style="", no_wrap=True)
        table.add_column("Description", justify="left", style="", no_wrap=True)
        table.add_column("Value", justify="left", style="", no_wrap=True)
        for prop in rem.properties():
            table.add_row(prop.name, prop.description, str(prop.value))
        core.globals.console.print(table)

    data = [prop.model_dump() for prop in rem.properties()]
    if format == "json":
        core.globals.console.print_json(core.json.text(data))
    elif format in ("yml", "yaml"):
        core.globals.console.print(core.yaml.text({"properties": data}))


@remote.command(help="Upload files to remote environment")
@click.argument('items', required=False, nargs=-1)
@click.pass_context
def upload(ctx: click.Context, items: tuple[str]):
    rem: framework.remote.Interface = ctx.obj.get("instance")
    paths = split(items)
    if not paths:
        return
    rem.upload(paths)


@remote.command(help="Download files from remote environment")
@click.argument('items', required=False, nargs=-1)
@click.pass_context
def download(ctx: click.Context, items: tuple[str]):
    rem: framework.remote.Interface = ctx.obj.get("instance")
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
