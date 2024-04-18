import os

import asyncclick

from umk.application import utils

if not os.environ.get('_UMK_COMPLETE'):
    from umk import runtime, core
    from rich.table import Table
    from umk.framework.system.shell import Shell


@asyncclick.group()
@utils.options.remote
async def root(r):
    pass


@root.command(help="Run project targets")
@utils.options.config.all
@asyncclick.argument('names', required=True, nargs=-1)
def run(c: tuple[str], p: tuple[str], f: bool, names: tuple[str]):
    opt = runtime.Options()
    opt.config = utils.config(f, p, c)
    runtime.c.load(opt)
    utils.forward(runtime.c)
    runtime.c.targets.run(*names)


@root.command(name='inspect', help="Inspect project details")
@utils.options.style
@utils.options.config.all
def inspect(s: str, c: tuple[str], p: tuple[str], f: bool):
    opt = runtime.Options()
    opt.config = utils.config(f, p, c)
    runtime.c.load(opt)

    pro = runtime.c.project.instance
    tar = runtime.c.targets
    if s in ("style", ""):
        table_info = Table(
            title="INFO",
            title_style="bold cyan",
            title_justify="left",
            show_header=False,
            show_edge=False,
            show_lines=False,
            box=None,
        )
        table_info.add_column("Name", justify="left", style="bold", no_wrap=True)
        table_info.add_column("Value", justify="left", style="", no_wrap=True)
        table_info.add_row("• Id", pro.info.id)
        table_info.add_row("• Version", pro.info.version)
        table_info.add_row("• Name", pro.info.name)
        table_info.add_row("• Description", pro.info.description)

        if pro.info.contributors:
            table_contributors = Table(
                title="CONTRIBUTORS",
                title_style="bold cyan",
                title_justify="left",
                show_header=False,
                show_edge=False,
                show_lines=False,
                box=None,
            )
            table_contributors.add_column("Name", justify="left", style="bold", no_wrap=True)
            table_contributors.add_column("Value", justify="left", style="", no_wrap=True)
            for contrib in pro.info.contributors:
                contacts = " ".join(contrib.email)
                contacts += " " + " ".join([f'{k}:{v}' for k, v in contrib.socials.items()])
                table_contributors.add_row(f"• {contrib.name}", contacts)

        if tar:
            table_targets = Table(
                title="TARGETS",
                title_style="bold cyan",
                title_justify="left",
                show_header=False,
                show_edge=False,
                show_lines=False,
                box=None,
            )
            table_targets.add_column("Name", justify="left", style="bold", no_wrap=True)
            table_targets.add_column("Description", justify="left", style="", no_wrap=True)
            for t in tar:
                table_targets.add_row(f"• {t.name}", t.description)
        core.globals.console.print(table_info)
        if tar:
            core.globals.console.print()
            core.globals.console.print(table_targets)
        if pro.info.contributors:
            core.globals.console.print()
            core.globals.console.print(table_contributors)
    elif s == "json":
        # TODO Append targets
        core.globals.console.print_json(core.json.text(pro.info))


@root.command(help="Release project")
@utils.options.config.all
def release(c: tuple[str], p: tuple[str], f: bool):
    opt = runtime.Options()
    opt.config = utils.config(f, p, c)
    runtime.c.load(opt)
    utils.forward(runtime.c)
    runtime.c.project.release()


@root.command(name='format', help="Format .unimake/*.py files")
def prettier():
    if not core.globals.paths.unimake.exists():
        core.globals.console.print("[bold]No '.unimake' folder was found")
    else:
        sh = Shell()
        sh.name = "format"
        sh.cmd = ["black", "-l", "100", "-t", "py311", "-W", "4", core.globals.paths.unimake]
        sh.sync()
