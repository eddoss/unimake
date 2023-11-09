import asyncio
import unimake
from unimake import cli
from umk.globals import Global


try:
    asyncio.run(unimake.cli.application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
