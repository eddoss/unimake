from pathlib import Path

from fs.base import FS
from fs.osfs import OSFS
from fs.walk import Walker
from fs import move as _mv

from umk import core


@core.overload
def move(
    src: str | Path,
    dst: str | Path,
):
    """
    Moves file or directory to destination path (on local filesystem).
    It will create all destination sub-dirs if not exists.

    :param src: Path to file or directory to move from.
    :param dst: Path to file or directory to move to.

    Examples
    ::
     - move(Path('./main.py'), Path('./hello.py'))
     - move(Path('./hellp.py'), Path('./some/dir/hello.py'))
    """
    s = OSFS(src.parent.as_posix())
    d = OSFS(dst.parent.as_posix(), create=True)
    _mv.move_file(s, src.name, d, dst.name)


@core.overload
def move(
    src: str | Path,
    dst: tuple[FS, str]
):
    """
    Moves specific local file/directory to destination filesystem.
    It will create all destination sub-dirs if not exists.

    :param src: Source file/directory path
    :param dst: Tuple of filesystem to move to and path to file/directory in destination filesystem

    Examples
     - move('./some/file.txt', (ftp(..), 'description.ini'))
    """
    raise NotImplemented()


@core.overload
def move(
    src: tuple[FS, str],
    dst: str | Path
):
    """
    Moves specific file or directory from source filesystem to local file.
    It will create all destination sub-dirs if not exists.

    :param src: Tuple of filesystem to move from and path to file/directory in source filesystem
    :param dst: Destination file/directory path

    Examples
     - move((ftp(..), 'description.ini'), './some/file.txt')
    """
    raise NotImplemented()


@core.overload
def move(
    src: tuple[FS, str],
    dst: tuple[FS, str]
):
    """
    Moves specific file or directory from source FS to destination FS.
    It will create all destination sub-dirs if not exists.

    :param src: Tuple of filesystem to move from and path to file/directory in source filesystem
    :param dst: Tuple of filesystem to move to and path to file/directory in destination filesystem

    Examples
     - move(local(..), 'some/file.txt', ftp(..), 'file.txt')
    """
    raise NotImplemented()


@core.overload
def move(
    src: FS,
    dst: FS,
    wlk: Walker
):
    """
    Moves walker items from source FS to destination FS.
    It will create all destination sub-dirs if not exists.

    :param src: Filesystem to move from
    :param dst: Filesystem to move to
    :param wlk: Walker from source filesystem

    Examples:
     - move(local(..), ftp(..), walker(..))
    """
    raise NotImplemented()
