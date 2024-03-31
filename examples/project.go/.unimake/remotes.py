from umk.framework import project
from umk.framework import remote
from umk.framework import system
from umk.framework.adapters import docker


@remote.register
def development():
    pro: project.Golang = project.get()
    usr = system.user()

    dockerfile = docker.File(path=pro.layout.unimake)
    dockerfile.froms("ubuntu:latest")
    dockerfile.run([
        f"apt-get update",
        f"apt-get -y install sudo",
        f"mkdir -p /etc/sudoers.d",
        f'echo "{usr.name} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
        f"groupadd -g {usr.group.id} edward",
        f"useradd -m -u {usr.id} -d /home/{usr.name} -g {usr.group.id} -s /bin/sh {usr.name}"
    ])
    dockerfile.user(usr.id)
    dockerfile.env("PATH", f"$PATH:/home/{usr.name}/.local/bin")
    dockerfile.run([
        f"sudo chown {usr.name}:{usr.name} /home/{usr.name}",
        "sudo apt-get -y install make git python3 pip",
        "pip install poetry"
    ], separate=True)

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
    service.volumes.bind(
        src=pro.layout.root.parent.parent,
        dst=f"/home/{usr.name}/umk"
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
