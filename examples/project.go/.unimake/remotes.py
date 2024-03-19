from umk.framework import project
from umk.framework import remote
from umk.framework import system
from umk.framework.adapters import docker
from project import Project


@remote.register
def development():
    pro: Project = project.get()
    usr = system.user()

    dockerfile = docker.File(path=pro.layout.unimake)
    dockerfile.froms("ubuntu:latest")
    dockerfile.run([
        f"apt update",
        f"apt -y install sudo",
        f"mkdir -p /etc/sudoers.d",
        f'echo "{usr.name} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
        f"groupadd -g {usr.group.id} edward",
        f"useradd -m -u {usr.id} -d /home/{usr.name} -g {usr.group.id} -s /bin/sh {usr.name}"
    ])
    dockerfile.user(usr.id)
    dockerfile.run([f"sudo chown {usr.name}:{usr.name} /home/{usr.name}"])

    service = docker.ComposeService()
    service.build = docker.ComposeBuild()
    service.build.context = dockerfile.path
    service.build.dockerfile = dockerfile.name
    service.image = "unimake"
    service.container_name = "unimake"
    service.hostname = service.container_name
    service.working_dir = f"/home/{usr.name}/workdir"
    service.user = f"{usr.id}:{usr.group.id}"
    service.entrypoint = ["sleep", "infinity"]
    service.volumes.bind(
        src=pro.layout.root,
        dst=f"/home/{usr.name}/workdir"
    )

    result = remote.DockerCompose()
    result.name = "dev"
    result.default = True
    result.description = "Project development infrastructure"
    result.composefile.services[result.name] = service
    result.composefile.path = pro.layout.unimake
    result.service = result.name
    result.dockerfiles.append(dockerfile)

    return result


@remote.register
def container():
    result = remote.DockerContainer()
    result.container = "unimake"
    result.user = system.user()
    result.privileged = False
    result.workdir = f"/home/{result.user.name}/workdir"
    return result
