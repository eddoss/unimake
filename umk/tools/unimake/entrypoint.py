import asyncio
import os

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from umk import core
from umk.tools.unimake import application


if not os.environ.get('_UNIMAKE_COMPLETE', None):
    try:
        asyncio.run(application())
    except Exception as err:
        core.print_error(err)
else:
    asyncio.run(application())
