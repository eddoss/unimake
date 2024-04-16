import asyncio
from pathlib import Path

from umk.application import cmd
from umk.application.utils import State


cwd = Path.cwd()
uni = cwd / '.unimake'
if uni.exists():
    cli_file = uni / "cli.py"
    if cli_file.exists():
        import sys
        from importlib import util as importer
        s = importer.spec_from_file_location("cli", cli_file)
        m = importer.module_from_spec(s)
        sys.modules[f'umk:cli'] = m
        s.loader.exec_module(m)


if State.Complete or State.Unsafe:
    asyncio.run(cmd.root())
else:
    try:
        asyncio.run(cmd.root())
    except Exception as err:
        from umk import runtime
        runtime.errors(err)
