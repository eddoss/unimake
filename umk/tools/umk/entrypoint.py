import asyncio
import os
import sys
from umk import framework, dot, Global
from umk.tools.umk.application import application


framework.cli.cmd = application.command

Global.completion = os.environ.get('_UMK_COMPLETE')
if Global.completion:
    os.environ.pop('_UMK_COMPLETE')

state = None
try:
    state = dot.Instance.load(
        root=Global.paths.unimake,
        project=dot.OPT if Global.completion else dot.YES,
        cli=dot.OPT if Global.completion else dot.YES,
        remotes=dot.OPT,
    )
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
    sys.exit()

if not Global.completion and not state.ok:
    state.print()
    sys.exit(-1)

if Global.completion:
    os.environ['_UMK_COMPLETE'] = Global.completion

try:
    asyncio.run(application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
