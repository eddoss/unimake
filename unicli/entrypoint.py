import asyncio
import os
import sys
import umk.cli
from umk.dotunimake.instance import Require
from umk.dotunimake.implementation import Instance
from unicli.application import application
from umk.globals import Global


umk.cli.cmd = application.command

Global.completion = os.environ.get('_UMK_COMPLETE')
if Global.completion:
    os.environ.pop('_UMK_COMPLETE')

state = None
try:
    state = Instance.load(
        root=Global.paths.unimake,
        project=Require.OPT if Global.completion else Require.YES,
        cli=Require.OPT if Global.completion else Require.YES,
        remotes=Require.OPT,
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
