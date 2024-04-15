import asyncio
import os

from umk.application import cmd

com = "_UMK_COMPLETE" in os.environ
uns = "UMK_UNSAFE" in os.environ

if com or uns:
    asyncio.run(cmd.root())
else:
    try:
        asyncio.run(cmd.root())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
