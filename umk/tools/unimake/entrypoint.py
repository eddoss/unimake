import asyncio
import sys

from umk import globals
from umk.tools.unimake import application


try:
    asyncio.run(application())
except Exception:
    globals.console.print_exception(show_locals=False, max_frames=1)
    sys.exit(-1)
