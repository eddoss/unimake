import os
from pathlib import Path
from beartype.typing import Generator
from beartype import beartype


class Filesystem:
    @staticmethod
    @beartype
    def mkdir(path: os.PathLike, mode=0o777):
        """
        Creates a leaf directory and all intermediate ones
        :param path: path to directory to be created
        :param mode: directory mod (see chmod on unix)
        """
        # os.makedirs(name=path, mode=mode, exist_ok=True)
        print(path)

    @staticmethod
    @beartype
    def cp(src: os.PathLike, dst: os.PathLike):
        pass

    @staticmethod
    @beartype
    def listdir(directory: os.PathLike, types="fdl", paths=False) -> Generator[str, None, None]:
        """
        Iterate over all names in the given directory.
        You can skip any types by 'types' parameter.

        How 'types' work:
         - f - don't skip files
         - d - don't skip directories

        How to:
         - get file names: listdir(dir, 'f')
         - get folder paths: listdir(dir, 'd', True)
         - get all paths: listdir(dir, paths=True)
         - get all names: listdir(dir)

        :param directory: path to the directory to lists
        :param types: content filter, see description for details
        :param paths: if true, this function will return full paths, just names otherwise
        :return: generator of the directory content
        """

        root = Path(directory)
        if not root.exists():
            return

        for name in os.listdir(root):
            path = Path(root, name)
            if 'f' in types and path.is_file():
                yield (name, path)[int(paths)]
            elif 'd' in types and path.is_dir():
                yield (name, path)[int(paths)]
