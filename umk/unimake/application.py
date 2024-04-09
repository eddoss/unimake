import os

import asyncclick

if not os.environ.get('_UNIMAKE_COMPLETE'):
    from umk import runtime, core
from umk.unimake import utils


@asyncclick.group()
async def application():
    pass


@application.group(cls=utils.ConfigableCommand, help="Run project action")
@asyncclick.option("--remote", default=None, help="Execute command in specific remote environment")
@asyncclick.option("-R", is_flag=True, default=False, help="Execute command in default remote environment. This flag has higher priority than --remote")
@asyncclick.argument('names', required=True, nargs=-1)
@asyncclick.pass_context
def action(ctx: asyncclick.Context, remote: str, r: bool, c: list[str], p: str, f: bool, names: tuple[str]):
    locally = not bool(remote or r)

    lo = runtime.LoadingOptions()
    lo.config.overrides = utils.parse_config_overrides(c)
    lo.config.preset = p or ""
    lo.config.file = f
    lo.modules.project = runtime.YES
    lo.modules.config = runtime.OPT
    lo.modules.remotes = runtime.NO if locally else runtime.NO
    runtime.load(lo)

    if not locally:
        rem = utils.find_remote(r, remote)
        rem.execute(cmd=["unimake", "action"] + list(names))
        ctx.exit()

    valid = []
    for name in names:
        func = runtime.container.project.actions.get(name)
        if not func:
            core.globals.console.print(f"[yellow bold]Action '{name}' not found")
        else:
            valid.append(name)

    for name in valid:
        runtime.container.project.run(name)
