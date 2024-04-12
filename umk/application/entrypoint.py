import asyncio
import os

from umk.application.root import root
from umk.application import cmd

if os.environ.get('_UMK_COMPLETE', None):
    asyncio.run(root())
else:
    try:
        asyncio.run(root())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
# asyncio.run(root())
