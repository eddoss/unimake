import zipfile

from beartype.typing import Any, Union, BinaryIO, Optional
from beartype import beartype

from fs import open_fs
from fs.base import FS
from fs.osfs import OSFS
from fs.ftpfs import FTPFS
from fs.zipfs import ZipFS
from fs.tarfs import TarFS
from fs.tempfs import TempFS
from fs.memoryfs import MemoryFS
from fs.subfs import SubFS


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
