import zipfile
from pathlib import Path

from beartype.typing import Any, Union, BinaryIO, Optional
from beartype import beartype

from fs import open_fs
from fs.walk import Walker
from fs.base import FS
from fs import copy as cp
from fs import move as mv
from fs.osfs import OSFS
from fs.ftpfs import FTPFS
from fs.zipfs import ZipFS
from fs.tarfs import TarFS
from fs.tempfs import TempFS
from fs.memoryfs import MemoryFS
from fs.subfs import SubFS

from multimethod import overload


@beartype
def generic(url: str, writeable: bool = False, create: bool = False, cwd: str = '.') -> FS:
    """
    Open any filesystem
    """
    return open_fs(url, writeable, create, cwd)


@beartype
def local(root='.', create=False, mode=0o777, expand_vars=True) -> OSFS:
    """
    Open local filesystem
    """
    return OSFS(root_path=root, create=create, create_mode=mode, expand_vars=expand_vars)


@beartype
def ftp(host: str, user="anonymous", passwd="", acct="", timeout=10, port=21, proxy=None, tls=False):
    """
    Open FTP filesystem
    """
    return FTPFS(host, user, passwd, acct, timeout, port, proxy, tls)


@beartype
def tar(file: Union[str, BinaryIO], write=False, compression: Optional[str] = None, encoding="utf-8") -> TarFS:
    """
    Open tar archive
    """
    return TarFS(file, write, compression, encoding)


@beartype
def zip(file: Union[str, BinaryIO], write=False, compression=zipfile.ZIP_DEFLATED, encoding="utf-8") -> ZipFS:
    """
    Open zip archive
    """
    return ZipFS(file, write, compression, encoding)


@beartype
def tmp(ident: str, directory: str) -> TempFS:
    """
    Open filesystem in temporary directory
    """
    return TempFS(ident, directory)


@beartype
def memory() -> MemoryFS:
    """
    Open in-memory filesystem
    """
    return MemoryFS()


@beartype
def sub(parent: FS, path: str) -> Any:
    return SubFS(parent, path)


@overload
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
    pass


@overload
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
    pass


@overload
def copy(
    src: Union[str, Path],
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
    pass


@overload
def copy(
    src: tuple[FS, str],
    dst: Union[str, Path],
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
    pass


@overload
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
    pass


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
    pass


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
    pass


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
    pass


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
    pass


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
    pass


class Installer:
    @beartype
    def __init__(self, root: Path):
        self._root = local(root.expanduser().resolve().absolute().as_posix())

    def __enter__(self) -> 'Installer':
        """Allow use of install as a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close installer on exit."""
        self.close()

    def close(self):
        self._root.close()

    @beartype
    def add(
        self,
        path: Union[str, Path],
        name: str = '',
        timestamp: bool = True,
        group: str = '',
        mode: str = '',
        owner: str = ''
    ):
        """
        Copies given file/directory to root with new name.
        If new name is empty, source file/directory name will be used.

        :param path: File/directory to copy
        :param name: New file/directory name. Leave it empty to use source name.
        :param timestamp: Preserve timestamp or not
        :param group: Destination file mode.
        :param mode: Destination file group.
        :param owner: Destination file ownership (required super-user permission).
        """
        p = Path(path)
        n = name
        if not name:
            n = p.name
        copy(
            src=path,
            dst=(self._root, n),
            timestamp=timestamp,
            group=group,
            mode=mode,
            owner=owner
        )
