import os

import asyncclick

if not os.environ.get('_UMK_COMPLETE'):
    from umk import runtime, core
    from rich.table import Table
    from umk.application import utils
from umk.application.utils import ConfigableCommand


@asyncclick.group()
async def root():
    pass


@root.command(cls=ConfigableCommand, name='inspect', help="Inspect project details")
@asyncclick.option('--format', '-f', default="style", type=asyncclick.Choice(["style", "json"], case_sensitive=False), help="Output format")
def inspect(format: str, c: tuple[str], p: tuple[str], f: bool):
    opt = runtime.Options()
    opt.config.overrides = utils.parse_config_overrides(c)
    opt.config.presets = list(p)
    opt.config.file = f
    runtime.c.load(opt)

    pro = runtime.c.project.instance
    if format in ("style", ""):
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

        core.globals.console.print(table_info)
        if pro.info.contributors:
            core.globals.console.print()
            core.globals.console.print(table_contributors)
    elif format == "json":
        core.globals.console.print_json(core.json.text(pro.info))
