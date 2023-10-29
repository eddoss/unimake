import asyncio
import os
import umk.cli
from umk.globals import Global


Global.completion = '_UMK_COMPLETE' in os.environ

umk.cli.unimake = umk.cli.DotUnimake(Global.paths.unimake)
umk.cli.unimake.validate()
umk.cli.unimake.load_dotenv()
umk.cli.unimake.load_project()
umk.cli.unimake.load_cli()

try:
    asyncio.run(umk.cli.application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
