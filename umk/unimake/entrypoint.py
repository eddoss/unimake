import asyncio
import os

from umk.unimake.application import application


if os.environ.get('_UNIMAKE_COMPLETE', None):
    asyncio.run(application())
else:
    try:
        asyncio.run(application())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
