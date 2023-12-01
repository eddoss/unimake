from beartype.typing import Optional
import umk.remote
from umk.project import Project
from umk.dotunimake.dotunimake import DotUnimake


Instance: Optional[DotUnimake] = DotUnimake()


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


umk.project = get_project
