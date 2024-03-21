from pathlib import Path

from .copy import copy
from .factories import generic, memory, local, zip, ftp, tmp, sub
from .move import move

AnyPath = Path | str
OptPath = Path | str | None
