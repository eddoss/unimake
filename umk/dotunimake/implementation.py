import umk.remote
from umk.project.base import Project
from umk.dotunimake.instance import ProjectInstance
from beartype.typing import Optional


Instance: Optional[ProjectInstance] = ProjectInstance()


# ####################################################################################
# Remote environment utils implementation
# ####################################################################################

def find_remote(name: str = "") -> Optional[umk.remote.Interface]:
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


umk.remote.find = find_remote
umk.remote.iterate = iterate_remotes


# ####################################################################################
# Project stuff implementation
# ####################################################################################

def get_project() -> Optional[Project]:
    global Instance
    return Instance.project


umk.projects.base.get = get_project
umk.project = get_project
