from umk import core
from umk.framework.adapters import docker
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface
from umk.framework.system import Shell, Environs, User


class Compose(Interface):
    dockerfiles: list[docker.File] = core.Field(
        default_factory=list,
        description="Dockerfile objects."
    )
    composefile: None | docker.ComposeFile = core.Field(
        default_factory=docker.ComposeFile,
        description="Docker compose file object."
    )
    service: str = core.Field(
        default=None,
        description="Target compose service"
    )
    sh: list[str] = core.Field(
        default_factory=lambda: ["bash"],
        description="Shell command (sh, bash, zsh, ...)"
    )

    @property
    def client(self) -> docker.Client:
        return docker.Client(
            compose_files=[self.composefile.file]
        )

    @core.typeguard
    def build(self, *args, **kwargs):
        # save docker files
        for dockerfile in self.dockerfiles:
            dockerfile.save()

        # save compose file
        self.composefile.save()

        services = list(self.composefile.services.keys())

        # clear old
        self.client.compose.down(remove_orphans=True, remove_images="all", volumes=True, quiet=False)
        self.client.compose.rm(services=services, stop=True, volumes=True)

        # build images
        self.client.compose.build(services=services)

        # create containers
        self.client.compose.create(services=services, no_recreate=True)

    def destroy(self, *args, **kwargs):
        services = list(self.composefile.services.keys())
        self.client.compose.down(remove_orphans=True, remove_images="all", volumes=True, quiet=False)
        self.client.compose.rm(services=services, stop=True, volumes=True)

    @core.typeguard
    def up(self, *args, **kwargs):
        services = list(self.composefile.services.keys())
        self.client.compose.up(services=services, build=False, detach=True, remove_orphans=True)

    def down(self, *args, **kwargs):
        self.client.compose.down(remove_orphans=True, volumes=True, quiet=False)

    def shell(self, **kwargs):
        service = kwargs.get("service", self.service)
        self.client.compose.execute(
            service=service,
            command=self.sh,
            detach=False,
            tty=True,
        )

    @core.typeguard
    def execute(self, cmd: list[str], cwd: None | Path | str = None, env: None | Environs = None, **kwargs):
        detach = kwargs.get("detach") or False
        self.client.compose.execute(
            service=self.service,
            command=cmd,
            envs=env,
            tty=False,
            workdir=cwd,
            detach=detach
        )

    @core.typeguard
    def upload(self, items: dict[str | Path, str | Path], **kwargs):
        service = kwargs.get("service", self.service)
        for i, (src, dst) in enumerate(items.items()):
            shell = Shell(cmd=self.client.compose.docker_compose_cmd)
            shell.cmd += ["cp", str(src), f"{service}:{dst}"]
            shell.sync(log=False)

    @core.typeguard
    def download(self, items: dict[str | Path, str | Path], **kwargs):
        service = kwargs.get("service", self.service)
        for i, (src, dst) in enumerate(items.items()):
            shell = Shell(cmd=self.client.compose.docker_compose_cmd)
            shell.cmd += ["cp", f"{service}:{src}", str(dst)]
            shell.sync(log=False)


class Container(Interface):
    container: str = core.Field(
        default="",
        description="Target container name",
    )
    sh: list[str] = core.Field(
        default_factory=lambda: ["bash"],
        description="Shell command (sh, bash, zsh, ...)"
    )
    workdir: str | Path = core.Field(
        default="/",
        description="Shell working directory."
    )
    environments: None | Environs = core.Field(
        default=None,
        description="Shell environment variables."
    )
    privileged: bool = core.Field(
        default=False,
        description="Open privileged shell."
    )
    user: None | User = core.Field(
        default=None,
        description="Open shell by user."
    )

    @property
    def client(self) -> docker.Client:
        return docker.Client()

    def shell(self, *args, **kwargs):
        user = None
        if self.user:
            user = f"{self.user.id}:{self.user.group.id}"
        self.client.container.execute(
            container=self.container,
            command=self.sh,
            detach=False,
            envs=self.environments or {},
            interactive=True,
            privileged=self.privileged,
            tty=True,
            user=user,
            workdir=self.workdir,
            stream=False
        )

    @core.typeguard
    def execute(self, cmd: list[str], cwd: None | Path | str = None, env: None | Environs = None, **kwargs):
        envs = {}
        if self.environments:
            envs.update(self.environments)
        if env:
            envs.update(env)
        if not envs:
            envs = None
        user = None
        if self.user:
            user = f"{self.user.id}:{self.user.group.id}"
        detach = kwargs.get("detach") or False
        self.client.container.execute(
            container=self.container,
            command=self.sh + cmd,
            detach=detach,
            envs=envs,
            interactive=False,
            privileged=self.privileged,
            tty=False,
            user=user,
            workdir=self.workdir,
            stream=False
        )

    @core.typeguard
    def upload(self, items: dict[str | Path, str | Path], **kwargs):
        for i, (src, dst) in items.items():
            self.client.container.copy(
                source=src,
                destination=(self.container, dst)
            )

    @core.typeguard
    def download(self, items: dict[str | Path, str | Path], **kwargs):
        for i, (src, dst) in items.items():
            self.client.container.copy(
                source=(self.container, src),
                destination=dst
            )


if __name__ == '__main__':
    from umk.framework.system import user

    u = user()
    dockerfile = docker.File()
    dockerfile.froms("ubuntu:latest")
    dockerfile.run([
        f"apt update",
        f"apt -y install sudo",
        f"mkdir -p /etc/sudoers.d",
        f'echo "{u.name} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
        f"groupadd -g {u.group.id} edward",
        f"useradd -m -u {u.id} -d /home/{u.name} -g {u.group.id} -s /bin/sh {u.name}"
    ])
    dockerfile.user(str(u.id))
    dockerfile.run([f"sudo chown {u.name}:{u.name} /home/{u.name}"])
    dockerfile.path = Path("~/astra/projects/umk/docker").expanduser()

    development = docker.ComposeService()
    development.build = docker.ComposeBuild()
    development.build.context = dockerfile.path
    development.build.dockerfile = dockerfile.name
    development.image = "unimake"
    development.container_name = "unimake"
    development.hostname = development.container_name
    development.working_dir = f"/home/{u.name}/workdir"
    development.user = f"{u.id}:{u.group.id}"
    development.entrypoint = ["sleep", "infinity"]
    development.volumes.bind(
        src="/home/edward/astra/projects/umk",
        dst="/home/edward/workdir"
    )

    composefile = docker.ComposeFile()
    composefile.services["development"] = development
    composefile.path = dockerfile.path

    comp = Compose()
    comp.description = "Development services for building, testing, debugging, etc."
    comp.dockerfiles.append(dockerfile)
    comp.service = "development"
    comp.composefile = composefile
    comp.sh = ["bash"]

    comp.build()
    comp.up()
    comp.shell()
    comp.destroy()

    cont = Container()
    cont.container = "unimake"
    cont.user = u
    cont.privileged = False
    cont.workdir = "/home/edward/workdir"

    # cont.shell()
