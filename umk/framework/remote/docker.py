import sys

from umk import core
from umk.framework.adapters import docker
from umk.framework.filesystem import AnyPath, OptPath
from umk.framework.remote.interface import Interface
from umk.framework.system.environs import OptEnv
from umk.framework.system.shell import Shell
from umk.framework.system.user import User


class Login(core.Model):
    server: str = core.Field(default="", description="Server URL")
    user: str = core.Field(default="", description="Docker repository user")
    password: str = core.Field(default="", description="Docker repository password")


class Compose(Interface):
    service: str = core.Field(
        default=None,
        description="Target compose service"
    )
    sh: list[str] = core.Field(
        default_factory=lambda: ["bash"],
        description="Shell command (sh, bash, zsh, ...)"
    )
    tty: bool = core.Field(
        default_factory=lambda: sys.stdout.isatty(),
        description="Instantiate tty when call 'execute'"
    )
    composefile: None | docker.ComposeFile = core.Field(
        default_factory=docker.ComposeFile,
        description="Docker compose file object."
    )
    dockerfiles: list[docker.File] = core.Field(
        default_factory=list,
        description="Dockerfile objects."
    )
    logins: list[Login] = core.Field(
        default_factory=list,
        description="Private repositories login info"
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

    def login(self, **kwargs):
        if not self.logins:
            core.globals.console.print(
                "[bold]No private repositories to login to !"
            )
            return
        for info in self.logins:
            core.globals.console.print(f"Docker login: '{info.server}'")
            self.client.login(info.server, info.user, info.password)

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
    def execute(self, cmd: list[AnyPath], cwd: OptPath = None, env: OptEnv = None, **kwargs):
        detach = kwargs.get("detach") or False
        self.client.compose.execute(
            service=self.service,
            command=cmd,
            envs=env or {},
            tty=self.tty,
            workdir=cwd,
            detach=detach
        )

    @core.typeguard
    def upload(self, items: dict[AnyPath, AnyPath], **kwargs):
        service = kwargs.get("service", self.service)
        for i, (src, dst) in enumerate(items.items()):
            shell = Shell(cmd=self.client.compose.docker_compose_cmd)
            shell.cmd += ["cp", str(src), f"{service}:{dst}"]
            shell.sync(log=False)

    @core.typeguard
    def download(self, items: dict[AnyPath, AnyPath], **kwargs):
        service = kwargs.get("service", self.service)
        for i, (src, dst) in enumerate(items.items()):
            shell = Shell(cmd=self.client.compose.docker_compose_cmd)
            shell.cmd += ["cp", f"{service}:{src}", str(dst)]
            shell.sync(log=False)

    def property(self, name: str) -> list[core.Property]:
        if name != "dockerfiles":
            return super().property(name)
        return [
            core.Property(
                name=f"dockerfile[{i}]",
                description=f"Dockerfile object [{i}]",
                value=df
            ) for i, df in enumerate(self.dockerfiles, start=0)
        ]


class Container(Interface):
    container: str = core.Field(
        default="",
        description="Target container name",
    )
    sh: list[str] = core.Field(
        default_factory=lambda: ["bash"],
        description="Shell command (sh, bash, zsh, ...)"
    )
    workdir: OptPath = core.Field(
        default="/",
        description="Shell working directory."
    )
    environments: OptEnv = core.Field(
        default=None,
        description="Shell environment variables."
    )
    privileged: bool = core.Field(
        default=False,
        description="Open privileged shell."
    )
    user: User | None = core.Field(
        default=None,
        description="Open shell by user."
    )

    @property
    def client(self) -> docker.Client:
        return docker.Client()

    def shell(self, *args, **kwargs):
        usr = None
        if self.user:
            usr = f"{self.user.id}:{self.user.group.id}"
        self.client.container.execute(
            container=self.container,
            command=self.sh,
            detach=False,
            envs=self.environments or {},
            interactive=True,
            privileged=self.privileged,
            tty=True,
            user=usr,
            workdir=self.workdir,
            stream=False
        )

    @core.typeguard
    def execute(self, cmd: list[AnyPath], cwd: OptPath = None, env: OptEnv = None, **kwargs):
        envs = {}
        if self.environments:
            envs.update(self.environments)
        if env:
            envs.update(env)
        if not envs:
            envs = None
        usr = None
        if self.user:
            usr = f"{self.user.id}:{self.user.group.id}"
        detach = kwargs.get("detach") or False
        self.client.container.execute(
            container=self.container,
            command=self.sh + cmd,
            detach=detach,
            envs=envs,
            interactive=False,
            privileged=self.privileged,
            tty=False,
            user=usr,
            workdir=self.workdir,
            stream=False
        )

    @core.typeguard
    def upload(self, items: dict[AnyPath, AnyPath], **kwargs):
        for i, (src, dst) in items.items():
            self.client.container.copy(
                source=src,
                destination=(self.container, dst)
            )

    @core.typeguard
    def download(self, items: dict[AnyPath, AnyPath], **kwargs):
        for i, (src, dst) in items.items():
            self.client.container.copy(
                source=(self.container, src),
                destination=dst
            )
