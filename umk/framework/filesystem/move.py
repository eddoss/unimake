from umk.framework.filesystem.path import Path

from beartype.typing import Union

from fs.walk import Walker
from fs.base import FS
from fs import move as mv

from multimethod import overload


@overload
def move(
    src: Union[str, Path],
    dst: Union[str, Path],
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
    raise NotImplemented()


@overload
def move(
    src: Union[str, Path],
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


@overload
def move(
    src: tuple[FS, str],
    dst: Union[str, Path]
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


@overload
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


@overload
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
