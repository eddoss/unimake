import os
import sys

import asyncclick as click

from umk.tools.unimake import application

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import runtime, framework, core
    from umk.tools import utils


@application.group(
    help="Project management commands",
    invoke_without_command=False,
    no_args_is_help=True,
    add_help_option=True,
)
@click.option("--remote", default=None, help="Execute command in specific remote environment")
@click.option("-R", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@click.pass_context
def project(ctx: click.Context, remote: str, r: bool):
    locally = not bool(remote or r)
    runtime.load(
        root=core.globals.paths.unimake,
        project=runtime.YES,
        config=runtime.OPT,
        remotes=[runtime.YES, runtime.NO][int(locally)]
    )
    if not locally:
        rem = utils.find_remote(r, remote)
        rem.execute(cmd=["unimake", "project"] + utils.subcmd(ctx.invoked_subcommand))
        ctx.exit()


@project.command(name='clean', help="Run project clean")
def clean():
    framework.project.run("clean")


@project.command(name='build', help="Run project building")
def build():
    framework.project.run("build")


@project.command(name='lint', help="Run project linting")
def lint():
    framework.project.run("lint")


@project.command(name='format', help="Run project formatting")
def formatting():
    framework.project.run("format")


@project.command(name='generate', help="Run project code generation")
def generate():
    framework.project.run('generate')


@project.command(name='documentation', help="Run project documentation generation")
def documentation():
    framework.project.run('documentation')


@project.command(name='bundle', help="Run project bundling")
def bundle():
    framework.project.run('bundle')


@project.command(name='release', help="Run project releasing")
def release():
    framework.project.run('release')


@project.command(name='test', help="Run project testing")
def run_testing():
    framework.project.run('test')


@project.command(name='inspect', help="Print project details")
@click.option('--format', '-f', default="style", type=click.Choice(["style", "json", "yaml"], case_sensitive=False), help="Output format")
def inspect(format: str):
    pro = runtime.container.project.object
    if format in ("style", ""):
        table_info = Table(
            title="INFO",
            title_style="bold",
            title_justify="left",
            show_header=False,
            show_edge=False,
            show_lines=False,
            box=None,
        )
        table_info.add_column("Name", justify="left", style="bold", no_wrap=True)
        table_info.add_column("Value", justify="left", style="", no_wrap=True)
        table_info.add_row("Id", pro.info.id)
        table_info.add_row("Version", pro.info.version)
        table_info.add_row("Name", pro.info.name)
        table_info.add_row("Description", pro.info.description)
        table_authors = Table(
            title="CONTRIBUTORS",
            title_style="bold",
            title_justify="left",
            show_header=False,
            show_edge=False,
            show_lines=False,
            box=None,
        )
        table_authors.add_column("Name", justify="left", style="bold", no_wrap=True)
        table_authors.add_column("Value", justify="left", style="", no_wrap=True)
        for contrib in pro.info.contributors:
            contacts = " ".join(contrib.email)
            contacts += " " + " ".join([f'{k}:{v}' for k, v in contrib.socials.items()])
            table_authors.add_row(contrib.name, contacts)

        core.globals.console.print(table_info)
        core.globals.console.print()
        core.globals.console.print(table_authors)
    elif format == "json":
        core.globals.console.print_json(core.json.text(pro.info))
    elif format == "yaml":
        core.globals.console.print(core.yaml.text(pro.info))


    # data = [prop.model_dump() for prop in rem.properties()]
    # if format == "json":
    #     core.globals.console.print_json(core.json.text(data))
    # elif format in ("yml", "yaml"):
    #     core.globals.console.print(core.yaml.text({"properties": data}))
