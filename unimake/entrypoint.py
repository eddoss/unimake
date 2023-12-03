import asyncio
import beartype
beartype.BeartypeConf.is_color = False
from umk.globals import Global
from unimake import application


try:
    asyncio.run(application())
except Exception:
    Global.console.print_exception(show_locals=False, max_frames=1)
