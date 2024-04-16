from pathlib import Path

from umk.framework.filesystem.copy import copy as cp
from umk.framework.filesystem.move import move as mv
from umk.framework.filesystem.factories import generic, memory, local, zip, ftp, tmp, sub

AnyPath = Path | str
OptPath = Path | str | None
