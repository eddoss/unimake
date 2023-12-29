from umk.framework import remote, system, project
from project import Project


@remote.register
def container():
    return remote.DockerContainer(
        name="con",
        default=False,
        container='publisher.dev',
    )
