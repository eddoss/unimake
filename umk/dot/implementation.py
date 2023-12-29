from umk import framework, core
from umk.framework.project.base import Project
from umk.dot.instance import Dot


Instance: Dot | None = Dot()


# ####################################################################################
# Remote environment utils implementation
# ####################################################################################

@core.typeguard
def find_remote(name: str = "") -> framework.remote.Interface | None:
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

def get_project() -> Project | None:
    global Instance
    return Instance.project


framework.project.get = get_project
