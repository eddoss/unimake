import asyncio

from umk import core
from umk.tools.unimake import application

try:
    asyncio.run(application())
except Exception as err:
    core.print_error(err)
