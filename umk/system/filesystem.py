import zipfile
from pathlib import Path

from beartype.typing import Any, Union, BinaryIO, Optional
from beartype import beartype

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

from multipledispatch import dispatch as overload


OptStr = Optional[str]


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


@beartype
@overload(Path, Path, bool, OptStr, OptStr, OptStr)
def copy(
    src: Path,
    dst: Path,
    timestamp: bool = True,
    group: OptStr = None,
    mode: OptStr = None,
    owner: OptStr = None
):
    """
    Copies file or directory to destination path (on local filesystem).
    It will create all destination sub-dirs if not exists.
    If mode/group/owner is None, it will be skipped.

    :param src: Source path to file or directory
    :param dst: Destination file or directory path
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param group: Destination file group.
    :param group: Destination file ownership (required super-user permission).

    Examples
     - copy(Path('./main.py'), Path('./hello.py'))
     - copy(Path('./hellp.py'), Path('./some/dir/hello.py'))
    """
    pass


@beartype
@overload(FS, str, FS, str, OptStr, OptStr, OptStr)
def copy(
    src_fs: FS,
    src_name: str,
    dst_fs: Path,
    dst_name: str,
    timestamp: bool = True,
    group: OptStr = None,
    mode: OptStr = None,
    owner: OptStr = None
):
    """
    Copies specific file or directory from source FS to destination FS.
    It will create all destination sub-dirs if not exists.
    If mode/group/owner is None, it will be skipped.

    :param src_fs: Filesystem to copy from
    :param src_name: Path to file/directory in source filesystem
    :param dst_fs: Filesystem to copy to
    :param dst_name: Path to file/directory in destination filesystem
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param group: Destination file group.
    :param group: Destination file ownership (required super-user permission).

    Examples
     - copy(local(..), 'some/file.txt', ftp(..), 'file.txt')
    """
    pass


@beartype
@overload(FS, FS, Walker, OptStr, OptStr, OptStr)
def copy(
    src: FS,
    dst: FS,
    walker: Walker,
    timestamp: bool = True,
    group: OptStr = None,
    mode: OptStr = None,
    owner: OptStr = None
):
    """
    Copies 'walker' items from source FS to destination FS.
    It will create all destination sub-dirs if not exists.

    :param src: Filesystem to copy from
    :param dst: Filesystem to copy to
    :param walker: Walker from source filesystem
    :param timestamp: Preserve timestamp or not
    :param group: Destination file mode.
    :param group: Destination file group.
    :param group: Destination file ownership (required super-user permission).
    """
    pass


@beartype
@overload(Path, Path)
def move(src: Path, dst: Path):
    """
    Moves file or directory to destination path (on local filesystem).
    It will create all destination sub-dirs if not exists.

    :param src: Path to file or directory to move from
    :param dst: Path to file or directory to move to

    Examples
     - move(Path('./main.py'), Path('./hello.py'))
     - move(Path('./hellp.py'), Path('./some/dir/hello.py'))
    """
    pass


@beartype
@overload(FS, str, FS, str)
def move(src_fs: FS, src_name: str, dst_fs: Path, dst_name: str):
    """
    Moves specific file or directory from source FS to destination FS.
    It will create all destination sub-dirs if not exists.

    :param src_fs: Filesystem to move from
    :param src_name: Path to file/directory in source filesystem
    :param dst_fs: Filesystem to move to
    :param dst_name: Path to file/directory in destination filesystem

    Examples
     - move(local(..), 'some/file.txt', ftp(..), 'file.txt')
    """
    pass


@beartype
@overload(FS, FS, Walker)
def move(src: FS, dst: FS, walker: Walker):
    """
    Moves 'walker' items from source FS to destination FS.
    It will create all destination sub-dirs if not exists.

    :param src: Filesystem to move from
    :param dst: Filesystem to move to
    :param walker: Walker from source filesystem
    """
    pass
