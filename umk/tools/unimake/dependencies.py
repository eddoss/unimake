import os
import sys

import asyncclick as click

from umk.tools.unimake import application

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core


@application.group(
    help="Dependencies management commands",
    invoke_without_command=False,
    no_args_is_help=True,
    add_help_option=True,
)
def deps():
    pass


@deps.command(help="List dependency groups")
def groups():
    pass


@deps.command(help="Resolve dependencies (or specific group)")
@click.option('--groups', '-g', multiple=True, help="Groups to deal with")
@click.option('--items', '-i', multiple=True, help="Items to deal with")
def resolve():
    pass


@deps.command(help="Inspect dependency groups/group/item")
@click.option('--format', '-f', default="style", type=click.Choice(["style", "json", "yaml"], case_sensitive=False), help="Output format")
def inspect():
    pass
