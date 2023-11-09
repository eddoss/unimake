import asyncio
import os
import sys

from umk import dotunimake as du
from umk.cli.main import application
from umk.globals import Global


Global.completion = os.environ.get('_UMK_COMPLETE')
if Global.completion:
    os.environ.pop('_UMK_COMPLETE')

state = du.LoadingState.OK
try:
    state = du.Unimake.load(
        root=Global.paths.unimake,
        project=du.Require.OPT if Global.completion else du.Require.YES,
        cli=du.Require.OPT if Global.completion else du.Require.YES,
        env=du.Require.OPT,
        remotes=du.Require.OPT,
    )
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)

if not Global.completion and state != du.LoadingState.OK:
    du.LoadingStateMessages().on(state)
    sys.exit()

if Global.completion:
    os.environ['_UMK_COMPLETE'] = Global.completion

try:
    asyncio.run(application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
