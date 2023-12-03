from beartype import beartype
from git import Repo as Repository
from umk.globals import Global, Path


@beartype
def tag(repo: Repository, on_error: str) -> str:
    result = on_error
    if repo and repo.tags:
        result = repo.tags[0].name
    return result


@beartype
def repository(root: Path = Global.paths.work):
    return Repository(root)
