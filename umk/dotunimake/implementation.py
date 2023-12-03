import umk
from umk import framework
from umk.framework.project.base import Project
from umk.dotunimake.instance import DotInstance
from beartype.typing import Optional


Instance: Optional[DotInstance] = DotInstance()


# ####################################################################################
# Remote environment utils implementation
# ####################################################################################

def find_remote(name: str = "") -> Optional[framework.remote.Interface]:
    global Instance
    if not Instance:
        return
    if not name:
        for remote in Instance.remotes.values():
            if remote.default:
                return remote
    else:
        return Instance.remotes.get(name)


def iterate_remotes():
    global Instance
    for rem in Instance.remotes.values():
        yield rem


framework.remote.find = find_remote
framework.remote.iterate = iterate_remotes


# ####################################################################################
# Project stuff implementation
# ####################################################################################

def get_project() -> Optional[Project]:
    global Instance
    return Instance.project


framework.project.get = get_project
