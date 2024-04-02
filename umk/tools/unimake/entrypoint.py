import asyncio
import os

if not os.environ.get('_UNIMAKE_COMPLETE', None):
    from umk import runtime
from umk.tools.unimake import application


# if not os.environ.get('_UNIMAKE_COMPLETE', None):
#     try:
#         asyncio.run(application())
#     except Exception as err:
#         runtime.errors(err)
# else:
#     asyncio.run(application())
asyncio.run(application())
