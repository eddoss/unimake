from umk.kit import remote, project, system
from umk.kit.adapter import docker
from config import Config


@remote.docker.compose
def _(s: remote.DockerCompose, c: Config, p: project.Golang):
    s.name = "dev"
    s.description = "Project development container"
    s.default = True

    u = system.user()

    # Dockerfile
    f = docker.File(path=p.layout.root, name="dev.dockerfile")
    f.froms("ubuntu")
    if c.usermod:
        f.run([
            f"apt-get update",
            f"apt-get -y install sudo",
            f"mkdir -p /etc/sudoers.d",
            f'echo "{u.name} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
            f"groupadd -g {u.group.id} {u.name}",
            f"useradd -m -u {u.id} -d /home/{u.name} -g {u.group.id} -s /bin/sh {u.name}",
        ])
        f.user(u.id)
        f.env("PATH", f"$PATH:/home/{u.name}/.local/bin")
        f.run([f"sudo chown {u.name}:{u.name} /home/{u.name}"])
        f.run([
            "sudo apt-get -y install git",
            "sudo apt-get -y install python3",
            "sudo apt-get -y install pip",
        ])
    else:
        f.run([
            "apt-get -y install git",
            "apt-get -y install python3",
            "apt-get -y install pip",
        ])
    f.run(["pip install umk"])

    # Compose service
    b = docker.ComposeService()
    b.build = docker.ComposeBuild()
    b.build.context = f.path
    b.build.dockerfile = f.name
    b.image = "project-image"
    b.container_name = "dev"
    b.ports = ["2233:2233"]
    b.hostname = "dev"
    b.working_dir = "/workdir"
    if c.usermod:
        b.user = f"{u.id}:{u.group.id}"
        b.working_dir = f"/home/{u.name}/workdir"
    b.volumes.bind(src=p.layout.root, dst=b.working_dir)
    b.entrypoint = ["sleep", "infinity"]

    s.dockerfiles.append(f)
    s.composefile.services["dev"] = b
    s.composefile.name = "dev.docker-compose.yaml"
    s.composefile.path = p.layout.root
    s.service = "dev"
