from umk import core
from umk.framework.filesystem.path import Path
from fs.walk import Walker
from fs.base import FS


@core.overload
def copy(
    src: Path,
    dst: Path,
    timestamp: bool = True,
    group: str = '',
    mode: str = '',
    owner: str = ''
):
    """
    Copies file or directory to destination path (on local filesystem).
    It will create all destination sub-dirs if not exists.
    If mode/group/owner is None, it will be skipped.

    :param src: Path to file or directory to move from.
    :param dst: Path to file or directory to move to.
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param mode: Destination file group.
    :param owner: Destination file ownership (required super-user permission).

    Examples
    ::
     - copy(Path('./main.py'), Path('./hello.py'))
     - copy(Path('./hellp.py'), Path('./some/dir/hello.py'))
    """
    raise NotImplemented()


@core.overload
def copy(
    src: tuple[FS, str],
    dst: tuple[FS, str],
    timestamp: bool = True,
    group: str = '',
    mode: str = '',
    owner: str = ''
):
    """
    Copies specific file or directory from source FS to destination FS.
    It will create all destination sub-dirs if not exists.
    If mode/group/owner is None, it will be skipped.

    :param src: Tuple of filesystem to copy from and path to file/directory in source filesystem
    :param dst: Tuple of filesystem to copy to and path to file/directory in destination filesystem
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param mode: Destination file group.
    :param owner: Destination file ownership (required super-user permission).

    Examples
     - copy(local(..), 'some/file.txt', ftp(..), 'file.txt')
    """
    raise NotImplemented()


@core.overload
def copy(
    src: str | Path,
    dst: tuple[FS, str],
    timestamp: bool = True,
    group: str = '',
    mode: str = '',
    owner: str = ''
):
    """
    Copies specific local file/directory to destination filesystem.
    It will create all destination sub-dirs if not exists.

    :param src: Source file/directory path
    :param dst: Tuple of filesystem to copy to and path to file/directory in destination filesystem
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param mode: Destination file group.
    :param owner: Destination file ownership (required super-user permission).

    Examples
     - copy('./some/file.txt', (ftp(..), 'description.ini'))
    """
    raise NotImplemented()


@core.overload
def copy(
    src: tuple[FS, str],
    dst: str | Path,
    timestamp: bool = True,
    group: str = '',
    mode: str = '',
    owner: str = ''
):
    """
    Copies specific file or directory from source filesystem to local file.
    It will create all destination sub-dirs if not exists.

    :param src: Tuple of filesystem to copy from and path to file/directory in source filesystem
    :param dst: Destination file/directory path
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param mode: Destination file group.
    :param owner: Destination file ownership (required super-user permission).

    Examples
     - copy((ftp(..), 'description.ini'), './some/file.txt')
    """
    raise NotImplemented()


@core.overload
def copy(
    src: FS,
    dst: FS,
    wlk: Walker,
    timestamp: bool = True,
    group: str = '',
    mode: str = '',
    owner: str = ''
):
    """
    Copies walker items from source FS to destination FS.
    It will create all destination sub-dirs if not exists.
    If mode/group/owner is None, it will be skipped.

    :param src: Filesystem to copy from
    :param dst: Filesystem to copy to
    :param wlk: Walker from source filesystem
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param mode: Destination file group.
    :param owner: Destination file ownership (required super-user permission).

    Examples:
    ::
     - copy(local(..), ftp(..), walker(..))
    """
    raise NotImplemented()
