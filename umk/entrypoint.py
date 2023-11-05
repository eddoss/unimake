import asyncio
import os
import umk.cli.main
from umk.cli.main import application
from umk.cli.dot_unimake import DotUnimake
from umk.globals import Global


Global.completion = '_UMK_COMPLETE' in os.environ

umk.cli.main.Unimake = DotUnimake(Global.paths.unimake)
umk.cli.main.Unimake.validate()
umk.cli.main.Unimake.load_dotenv()
umk.cli.main.Unimake.load_project()
umk.cli.main.Unimake.load_remotes()
umk.cli.main.Unimake.load_cli()

try:
    asyncio.run(application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
