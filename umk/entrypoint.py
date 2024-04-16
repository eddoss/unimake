import asyncio

from umk.application import cmd
from umk.application.utils import State

if State.Complete or State.Unsafe:
    asyncio.run(cmd.root())
else:
    try:
        asyncio.run(cmd.root())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
