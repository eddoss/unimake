from .copy import copy
from .factories import generic, memory, local, zip, ftp, tmp, sub
from .move import move
from .path import Path

AnyPath = Path | str
OptPath = Path | str | None
