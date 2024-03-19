import asyncio
import sys

from umk import globals
from umk.tools.unimake import application

try:
    asyncio.run(application())
except:
    globals.error_printer(sys.exception())
    sys.exit(-1)
