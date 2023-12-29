import asyncio
import os
import sys
from umk import framework, dot, globals
from umk.tools.umk.application import application


framework.cli.cmd = application.command

globals.completion = os.environ.get('_UMK_COMPLETE')
if globals.completion:
    os.environ.pop('_UMK_COMPLETE')

state = None
try:
    state = dot.Instance.load(
        root=globals.paths.unimake,
        project=dot.OPT if globals.completion else dot.YES,
        cli=dot.OPT if globals.completion else dot.YES,
        remotes=dot.OPT,
    )
except Exception:
    globals.console.print_exception(show_locals=False, max_frames=1)
    sys.exit()

if not globals.completion and not state.ok:
    state.print()
    sys.exit(-1)

if globals.completion:
    os.environ['_UMK_COMPLETE'] = globals.completion

try:
    asyncio.run(application())
except Exception:
    globals.console.print_exception(show_locals=False, max_frames=1)
