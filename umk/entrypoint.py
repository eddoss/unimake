from umk import state
from umk.application import cmd


if state.complete or state.unsafe:
    cmd.root()
else:
    try:
        cmd.root()
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
