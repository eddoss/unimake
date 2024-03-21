from git import Repo as Repository

from umk import core
from umk.framework.filesystem import Path


@core.typeguard
def tag(repo: Repository, on_error: str) -> str:
    result = on_error
    if repo and repo.tags:
        result = repo.tags[0].name
    return result


@core.typeguard
def repository(root: Path = core.globals.paths.work):
    return Repository(root)
