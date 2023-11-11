import asyncio
import sys

from umk.system import shell as sh


shell = sh.Shell(
    command=['docker', 'image', 'ls', '-a'],
    # descriptors=(None, None, sh.stdout),
    # descriptors=(None, sh.stdout, sh.stderr),
    descriptors=(None, sh.pipe, sh.pipe),
    handler=sh.ColorPrinter('[docker]', '[error]')
)
shell.sync()
