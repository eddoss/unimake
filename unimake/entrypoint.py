import asyncio
from pathlib import Path
import unimake
from unimake import cli
from umk.cli.dot_unimake import DotUnimake
from umk.globals import Global


root = Path.cwd() / '.unimake'
if root.exists():
    try:
        unimake.cli.common.unimake = DotUnimake(root)
        unimake.cli.common.unimake.load_dotenv()
        unimake.cli.common.unimake.load_remotes()
    except Exception as e:
        unimake.cli.common.unimake_loading_error = e
else:
    unimake.cli.common.no_unimake_folder = True

try:
    asyncio.run(unimake.cli.application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
