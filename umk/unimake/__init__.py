import asyncio
import os

from umk.unimake.root import root
from umk.unimake import cmd

# if os.environ.get('_UNIMAKE_COMPLETE', None):
#     asyncio.run(root())
# else:
#     try:
#         asyncio.run(root())
#     except Exception as err:
#         from umk import runtime
#         runtime.errors(err)
asyncio.run(root())
