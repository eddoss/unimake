import os
import tarfile
from pathlib import Path

from umk.core.typings import Optional

from umk import core
from umk.framework.system.user import User
from umk.framework.filesystem.copy import copy
from umk.framework.filesystem.factories import local, tar


class Installer:
    @core.typeguard
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

    @core.typeguard
    def install(
        self,
        path: str | Path,
        name: str = '',
        timestamp: bool = True,
        mode: Optional[int] = None,
        owner: Optional[User] = None
    ):
        """
        Copies given file/directory to root with new name.
        If new name is empty, source file/directory name will be used.

        :param path: File/directory to copy
        :param name: New file/directory name. Leave it empty to use source name.
        :param timestamp: Preserve timestamp or not
        :param mode: Destination file mode.
        :param owner: Destination file ownership (required super-user permission).
        """
        src = Path(path)
        dst = Path(os.path.join(self._root.root_path, name if name else src.name))
        copy(
            src=src,
            dst=dst,
            timestamp=timestamp,
        )
        if mode:
            os.chmod(dst, mode)
        if owner:
            os.chown(dst, owner.id, owner.group.id)


class Bundle(Installer):
    name: str = core.Field(
        default="bundle",
        description="Bundle name"
    )

    def tar(self, outdir: Path, compression: Optional[str] = None):
        if not outdir.exists():
            os.makedirs(outdir.as_posix())
        filename = f"{self.name}.tar"
        output = outdir / filename
        if output.exists():
            os.remove(output)
        cm = "w"
        if compression:
            cm += f":" + compression
        with tarfile.open(output, cm) as stream:
            root = Path(self._root.root_path)
            stream.add(root.as_posix(), arcname=root.name)