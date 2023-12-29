import shutil

import umk
from layout import Layout
from umk.framework import project, remote
from umk.framework.adapters import git, docker
from umk.framework.system import Environs, Shell, user
from umk.framework.filesystem import Path


class DockerRemote(remote.DockerContainer):
    def __init__(
        self,
        name: str = "",
        description: str = "Docker container environment",
        default: bool = False,
        container: str = "",
        shell: str = "sh",
    ):
        super().__init__(name, description, default, container, shell)
        self.image = ""
        self.file = Path()
        self.context = Path()
        self.build_args = {}
        self.volumes = {}

    def build(self, *args, **kwargs):
        client = docker.client()
        usr = user()
        try:
            client.images.build(
                fileobj=self.file.as_posix(),
                path=self.context.as_posix(),
                tag=self.image,
                forcerm=True,
                buildargs=self.build_args
            )
        except Exception as e:
            umk.print(e)
        try:
            client.containers.create(
                name=self.container,
                working_dir=f"/home/{usr.name}/workdir",
                user=usr.name,
                image=self.image,
                volumes=self.volumes
            )
        except Exception as e:
            umk.print(e)

    def destroy(self, *args, **kwargs):
        client = docker.client()
        try:
            client.images.remove(self.image)
        finally:
            pass
        cmd = self.cmd
        cmd.extend(["container", "rm", "-f", self.container])
        Shell(cmd).sync()

    def up(self, *args, **kwargs):
        cmd = self.cmd
        cmd.extend(["container", "start", self.container])
        Shell(cmd).sync()

    def down(self, *args, **kwargs):
        cmd = self.cmd
        cmd.extend(["container", "stop", self.container])
        Shell(cmd).sync()


class Development:
    def __init__(self, info: project.Info, layout: Layout):
        self.info = info
        self.docker = docker.client()
        self.layout = layout
        self.user = user()

    def image(self, *name: str):
        return f"dev.{self.info.name.full}." + ".".join(*name)

    def up(self):
        pass

    def down(self):
        pass

    def base_image(self):
        name = self.image("base")
        file = self.layout.dev / "images/base.dockerfile"
        try:
            self.docker.images.remove(name)
        finally:
            pass

        try:
            self.docker.images.build(
                fileobj=file.as_posix(),
                path=self.layout.root.as_posix(),
                tag=name,
                forcerm=True,
                buildargs={
                    "USER_ID": str(self.user.id),
                    "USER_NAME": self.user.name,
                    "GROUP_ID": self.user.group.id,
                    "GROUP_NAME": self.user.group.name,
                }
            )
        except Exception as e:
            umk.print(e)

    def golang_image(self):
        name = self.image("golang")
        file = self.layout.dev / "images/golang.dockerfile"
        try:
            self.docker.images.remove(name)
        finally:
            pass

        try:
            self.docker.images.remove(name)
            self.docker.images.build(
                fileobj=file.as_posix(),
                path=self.layout.root.as_posix(),
                tag=name,
                forcerm=True,
                buildargs={"BASE": self.image("base")}
            )
        except Exception as e:
            umk.print(e)

    def remote_ssh_image(self):
        rem = remote.DockerCompose(file=self.layout.dev / "remotes/ssh/docker-compose.yaml")
        rem.destroy()
        rem.build()
        rem.up()
        rem.execute(["umk install"])
        rem.down()

    # def remote_container_image(self):



@project.register
class Project(project.BaseProject):
    def __init__(self):
        super().__init__()
        self.git = git.Repository()
        self.layout = Layout()
        self.info.name.short = "umk"
        self.info.name.full = "unimake"
        self.info.version = git.tag(self.git, "unknown")
        self.info.authors = [
            project.Author('Edward Sarkisyan', 'edw.sarkisyan@gmail.com')
        ]
        self.info.description.short = \
            "Unimake is a set of development tools " \
            "and frameworks for project maintaining"
        self.dev = Development(self.info)

    def clean(self):
        """
        Remove project temporary stuff (cache, ...)
        """
        # Clean dist
        shutil.rmtree(self.layout.dist)
        # TODO Remove __pycache__ recursively

    def dependencies(self, dev: bool = False):
        """
        Install project dependencies
        """
        if dev:
            Shell(["poetry", "install"]).sync()
        else:
            Shell(["poetry", "install", "--with=dev"]).sync()

    def versionize(self):
        """
        Set project version (in pyproject.toml) from latest tag (do not call this manually)
        """
        # TODO Implement
        pass

    def build(self):
        """
        Build Python package
        """
        Shell(["poetry", "build"]).sync()

    def install(self):
        """
        Install framework and tools locally (Python package, umk and unimake)
        """
        Shell(["pip", "install", self.layout.dist / f"{self.info.name.short}-*.whl"]).sync()

    def uninstall(self):
        """
        Uninstall framework and tools locally
        """
        Shell(["pip", "uninstall", "--yes", self.info.name.short]).sync()

    def publish(self):
        """
        Publish project to private repository.
        """

        env = Environs()
        var = {
            "url": "PRIVATE_PYPI_URL",
            "usr": "PRIVATE_PYPI_USER",
            "pas": "PRIVATE_PYPI_PASSWORD",
        }

        url = env.get(var["url"], "").strip(),
        usr = env.get(var["usr"], "").strip(),
        pas = env.get(var["pas"], "").strip()

        if not url:
            umk.Global.console.print(
                f"[bold red]Failed to publish project. Repository URL is empty !\n"
                f"Specify it in '.env' by name {var['url']}"
            )
            return
        if not usr:
            umk.Global.console.print(
                f"[bold red]Failed to publish project. Repository user is empty !\n"
                f"Specify it in '.env' by name {var['usr']}"
            )
            return
        if not pas:
            umk.Global.console.print(
                f"[bold red]Failed to publish project. Repository password is empty !\n"
                f"Specify it in '.env' by name {var['pas']}"
            )
            return
        self.build()
        rep = f"{self.info.name.short}-internal"
        Shell(["poetry", "config", {rep}, url]).sync()
        Shell(["poetry", "config", f"http-basic.{rep}", usr, pas]).sync()
        Shell(["poetry", "publish", "--repository", rep]).sync()

    def format(self):
        """
        Format project python sources
        """
        Shell(["poetry", "run", "black", self.layout.src])
        Shell(["poetry", "run", "black", self.layout.tests])
        Shell(["poetry", "run", "black", self.layout.examples])
        Shell(["poetry", "run", "black", self.layout.umk])
