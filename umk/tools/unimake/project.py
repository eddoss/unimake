import os
import sys

import asyncclick as click

from umk.tools.unimake import application

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from rich.table import Table
    from umk import dot, framework, core


def find_remote_environment(default: bool, specific: str):
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


@application.group(
    help="Project management commands",
    invoke_without_command=False,
    no_args_is_help=True,
    add_help_option=True,
)
@click.option('--remote', default='', help="Execute command in specific remote environment")
@click.option("-r", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@click.pass_context
def project(ctx: click.Context, remote: str, r: bool):
    locally = not bool(remote or r)
    dot.Instance.load(
        root=core.globals.paths.unimake,
        project=dot.YES,
        remotes=[dot.YES, dot.NO][int(locally)]
    )
    if r or remote:  # Remote execution
        rem = find_remote_environment(r, remote)

        # Parse subcommand and its arguments
        subcmd = sys.argv[sys.argv.index(ctx.invoked_subcommand) + 1:]
        subcmd.insert(0, ctx.invoked_subcommand)
        subcmd.insert(0, 'unimake')

        # We skip rem.build() and rem.up() because remote environment must be built
        # and started by 'unimake remote ...'. We need just run the command.
        rem.execute(cmd=subcmd)
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
    pro = dot.Instance.container.project
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
