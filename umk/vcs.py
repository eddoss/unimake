from beartype import beartype
from git import Repo
from umk.globals import Global, Path

Git = Repo


@beartype
def tag(repo: Git, on_error: str) -> str:
    result = on_error
    if repo and repo.tags:
        result = repo.tags[0].name
    return result


@beartype
def git(root: Path = Global.paths.work):
    return Repo(root)
