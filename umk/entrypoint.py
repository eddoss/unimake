import asyncio

from umk import state
from umk.application import cmd


if state.complete or state.unsafe:
    asyncio.run(cmd.root())
else:
    try:
        asyncio.run(cmd.root())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
