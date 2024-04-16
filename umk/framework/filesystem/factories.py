import zipfile

from umk.core.typings import Any, BinaryIO
from fs import open_fs
from fs.base import FS
from fs.ftpfs import FTPFS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from fs.subfs import SubFS
from fs.tarfs import TarFS
from fs.tempfs import TempFS
from fs.zipfs import ZipFS

from umk import core


@core.typeguard
def generic(url: str, writeable: bool = False, create: bool = False, cwd: str = '.') -> FS:
    """
    Open any filesystem
    """
    return open_fs(url, writeable, create, cwd)


@core.typeguard
def local(root='.', create=False, mode=0o777, expand_vars=True) -> OSFS:
    """
    Open local filesystem
    """
    return OSFS(root_path=root, create=create, create_mode=mode, expand_vars=expand_vars)


@core.typeguard
def ftp(host: str, user="anonymous", passwd="", acct="", timeout=10, port=21, proxy=None, tls=False):
    """
    Open FTP filesystem
    """
    return FTPFS(host, user, passwd, acct, timeout, port, proxy, tls)


@core.typeguard
def tar(file: str | BinaryIO, write=False, compression: str | None = None, encoding="utf-8") -> TarFS:
    """
    Open tar archive
    """
    return TarFS(file, write, compression, encoding)


@core.typeguard
def zip(file: str | BinaryIO, write=False, compression=zipfile.ZIP_DEFLATED, encoding="utf-8") -> ZipFS:
    """
    Open zip archive
    """
    return ZipFS(file, write, compression, encoding)


@core.typeguard
def tmp(ident: str, directory: str) -> TempFS:
    """
    Open filesystem in temporary directory
    """
    return TempFS(ident, directory)


@core.typeguard
def memory() -> MemoryFS:
    """
    Open in-memory filesystem
    """
    return MemoryFS()


@core.typeguard
def sub(parent: FS, path: str) -> Any:
    return SubFS(parent, path)
