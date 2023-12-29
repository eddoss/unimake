from umk import core
from umk.framework.filesystem.path import Path
from umk.framework.filesystem.copy import copy
from umk.framework.filesystem.factories import local


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
    def add(
        self,
        path: str | Path,
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
