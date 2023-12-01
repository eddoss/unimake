import asyncio
import os
import sys
from umk.dotunimake import dotunimake as du
from umk.dotunimake import states as dus
from umk.dotunimake.instance import Instance as UniInstance
from umk.cli.main import application
from umk.globals import Global


Global.completion = os.environ.get('_UMK_COMPLETE')
if Global.completion:
    os.environ.pop('_UMK_COMPLETE')

state = dus.Ok()
try:
    state = UniInstance.load(
        root=Global.paths.unimake,
        project=du.Require.OPT if Global.completion else du.Require.YES,
        cli=du.Require.OPT if Global.completion else du.Require.YES,
        remotes=du.Require.OPT,
    )
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)

if not Global.completion and not state.ok:
    state.print()
    sys.exit()

if Global.completion:
    os.environ['_UMK_COMPLETE'] = Global.completion

try:
    asyncio.run(application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
