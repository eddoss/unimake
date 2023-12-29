from umk.framework import cli, remote, project, fs
from project import Project, Layout


proj: Project = project.get()
sections = {
    'bot': cli.Section('Bot', 'Bot target commands'),
    'pub': cli.Section('Publisher', 'Publisher target commands')
}


@cli.cmd(name="bot/build", section=sections['bot'], help="Build 'bot' target")
@cli.opt('--mode', default='debug')
async def bot_build(mode: str):
    await proj.build("bot", mode)


@cli.cmd(name="bot/debug", section=sections['bot'], help="Run debug server for 'bot' target")
@cli.opt('--port', default=2345)
def bot_debug(port: int):
    proj.debug("bot", port=port)


@cli.cmd(name="publisher/build", section=sections['pub'], help="Build 'publisher' target")
@cli.opt('--mode', default='debug', help='Build mode (debug, release)')
def publisher_build(mode: str):
    proj.build("publisher", mode)


@cli.cmd(help="Downloads Go dependencies and puts them to 'vendor'")
def vendor():
    proj.vendor()


@cli.cmd(help="Download binaries from development machine")
def download():
    a = Layout(fs.Path.home() / "workdir")
    b = proj.layout

    files = {
        (a.output / "bot").as_posix(): (b.root / "bot.exe").as_posix()
    }
    rem = remote.find()
    rem.download(files)


@cli.cmd(help="Upload source code to development virtual machine")
def upload():
    a = proj.layout
    b = Layout(fs.Path.home() / "workdir")

    files = {
        (a.cmd / "bot/main.go").as_posix(): (b.root / "bot.go").as_posix()
    }
    rem = remote.find()
    rem.upload(files)
