import os

from umk import globals, core
from umk.framework.remote.interface import Interface
from umk.framework.remote.interface import Events
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell
from umk.framework.adapters import docker
from umk.framework.adapters.docker.types import ImageBuildOptions
from umk.framework.adapters.docker.types import ContainerCreateOptions
from umk.framework.adapters.docker.file import File as Dockerfile


def create_docker_client() -> None | docker.Client:
    try:
        result = docker.client()
        return result
    except Exception as err:
        globals.close(err)


class ExistingContainer(Interface):
    client: None | docker.Client = core.Field(
        default_factory=create_docker_client,
        description="Docker daemon client"
    )
    command: list[str] = core.Field(
        default_factory=lambda: ["docker"],
        description="Docker CLI entrypoint",
    )
    container: str = core.Field(
        default="",
        description="Target container name",
    )
    sh: str = core.Field(
        default="bash",
        description="Default shell (bash, sh, zsh ...)"
    )

    def shell(self, *args, **kwargs):
        ed = core.EventData()
        ed.new("container", self.container, "Container name")
        ed.new("shell", self.container, "Shell name")
        if kwargs:
            ed.new("extra", kwargs, "Extra keyword arguments")
        globals.events.dispatch(
            Events.shell(before=True, instance=self, data=ed)
        )

        self.run("exec", "-i", "-t", self.container, self.sh).sync()

        globals.events.dispatch(
            Events.shell(before=False, instance=self, data=ed)
        )

    @core.typeguard
    def execute(self, cmd: list[str], cwd: str = "", env: envs.Optional = None, *args, **kwargs):
        ed = core.EventData()
        ed.new("container", self.container, "Container name")
        ed.new("shell", self.container, "Shell name")
        ed.new("command", cmd, "Command to execute")
        ed.new("workdir", cwd, "Working directory")
        ed.new("environs", env, "Environment variables")
        if kwargs:
            ed.new("extra", kwargs)
        globals.events.dispatch(
            Events.execute(before=True, instance=self, data=ed)
        )

        cmd = self.command.copy()
        cmd.extend(["exec", "-t"])
        if cwd:
            cmd.extend(["-w", cwd])
        if env:
            for k, v in env.items():
                cmd.extend(["-e", f"{k}={v}"])
        cmd.append(self.container)
        cmd.extend(cmd)
        self.run(*cmd).sync()

        globals.events.dispatch(
            Events.execute(before=False, instance=self, data=ed)
        )

    @core.typeguard
    def upload(self, items: dict[str, str], **kwargs):
        md = core.EventData()
        md.new("container", self.container, "Container name")
        md.new("items.count", len(items), "Items count")
        globals.events.dispatch(
            Events.upload(before=True, instance=self, data=md)
        )

        if not items:
            return

        i = 0
        for src, dst in items.items():
            ed = core.EventData()
            ed.new("container", self.container, "Container name")
            ed.new("item.index", i, "Item index")
            ed.new("item.src", src, "Item source path")
            ed.new("item.dst", dst, "Item destination path")
            globals.events.dispatch(
                Events.upload_item(before=True, instance=self, data=ed)
            )

            cmd = self.command.copy()
            cmd.extend(['container', 'cp', '-q', src, f"{self.container}:{dst}"])
            Shell(command=cmd, name=self.name, log=False).sync()

            globals.events.dispatch(
                Events.upload_item(before=False, instance=self, data=ed)
            )

            i += 1

        globals.events.dispatch(
            Events.upload(before=False, instance=self, data=md)
        )

    @core.typeguard
    def download(self, items: dict[str, str], **kwargs):
        md = core.EventData()
        md.new("container", self.container, "Container name")
        md.new("items.count", len(items), "Items count")
        globals.events.dispatch(
            Events.download(before=True, instance=self, data=md)
        )

        i = 0
        for src, dst in items.items():
            dst = Path(dst).expanduser().resolve().absolute()
            exs = dst.parent.exists()
            ed = core.EventData()
            ed.new("container", self.container, "Container name")
            ed.new("item.index", i, "Item index")
            ed.new("item.src", src, "Item source path")
            ed.new("item.dst", dst, "Item destination path")
            ed.new("item.dst.exists", exs, "Whether item destination folder path exists or not")
            globals.events.dispatch(
                Events.download_item(before=True, instance=self, data=ed)
            )

            if not exs:
                os.makedirs(dst.parent)

            self.run('container', 'cp', '-q', f"{self.container}:{src}", dst.as_posix(), log=False).sync()

            globals.events.dispatch(
                Events.download_item(before=False, instance=self, data=ed)
            )

            i += 1

        globals.events.dispatch(
            Events.download(before=False, instance=self, data=md)
        )

    @core.typeguard
    def run(self, *cmd: str, **shell) -> Shell:
        command = self.command.copy()
        command.extend(cmd)
        return Shell(cmd, name=self.name, **shell)


class BuildOptions(core.Object):
    file: Dockerfile = core.Field(
        default_factory=Dockerfile,
        description="Docker file object"
    )
    image: ImageBuildOptions = core.Field(
        default_factory=ImageBuildOptions,
        description="Image build options"
    )
    container: ContainerCreateOptions = core.Field(
        default_factory=ContainerCreateOptions,
        description="Container build parameters"
    )


class CustomContainer(ExistingContainer):
    options: BuildOptions = core.Field(
        default_factory=BuildOptions,
        description="Image and container build options"
    )

    def build(self, **kwargs):
        ed = core.EventData()
        ed.new("image.tag", self.options.image.tag, "Docker image name")
        ed.new("image.file", self.options.image.file, "Dockerfile output path")
        ed.new("container", self.options.container.name, "Docker container name")
        globals.events.dispatch(
            Events.build(before=True, instance=self, data=ed)
        )
        try:
            with open(self.options.image.file, "w") as stream:
                self.options.file.write(stream)
        except:
            pass
        try:
            image = self.client.images.get(self.options.image.tag)
            image.remove(force=True, noprune=False)
        except:
            pass
        try:
            options = self.options.image.to_native_params()
            self.client.images.build(**options)
            # self.client.images.prune(filters={"dangling": True})
        except Exception as err:
            globals.close(err)
        try:
            container = self.client.containers.get(self.options.container.name)
            container.remove(force=True)
        except:
            pass
        try:
            options = self.options.container.to_native_params()
            self.client.containers.create(self.options.image.tag, **options)
        except Exception as err:
            globals.close(err)
        globals.events.dispatch(
            Events.build(before=True, instance=self, data=ed)
        )

    def destroy(self, **kwargs):
        ed = core.EventData()
        ed.new("image.tag", self.options.image.tag, "Docker image name")
        ed.new("image.file", self.options.image.file, "Dockerfile output path")
        ed.new("container", self.options.container.name, "Docker container name")
        globals.events.dispatch(
            Events.destroy(before=True, instance=self, data=ed)
        )
        try:
            container = self.client.containers.get(self.options.container.name)
            container.stop()
            container.remove()
        except:
            pass
        try:
            image = self.client.images.get(self.options.image.tag)
            image.remove(force=True, noprune=False)
        except:
            pass

    def up(self, **kwargs):
        ed = core.EventData()
        ed.new("container", self.options.container.name, "Docker container name")
        globals.events.dispatch(
            Events.up(before=True, instance=self, data=ed)
        )
        try:
            container = self.client.containers.get(self.options.container.name)
            if container.status != "running":
                container.start()
        except Exception as err:
            globals.close(err)
        globals.events.dispatch(
            Events.up(before=True, instance=self, data=ed)
        )

    def down(self, **kwargs):
        ed = core.EventData()
        ed.new("container", self.options.container.name, "Docker container name")
        globals.events.dispatch(
            Events.down(before=True, instance=self, data=ed)
        )
        try:
            container = self.client.containers.get(self.options.container.name)
            if container.status == "running":
                container.stop()
        except Exception as err:
            globals.close(err)
        globals.events.dispatch(
            Events.down(before=True, instance=self, data=ed)
        )


if __name__ == '__main__':
    from umk.framework.filesystem import Path

    dockerfile = docker.File()
    dockerfile += docker.file.From(
        comment=["Base on astralinux"],
        image="aldev-devops-images.artifactory.astralinux.ru/astra:1.7.5"
    )
    dockerfile += docker.file.Run(
        space=1,
        comment=["Setup user"],
        commands=[
            f"apt update",
            f"apt -y install sudo",
            f"mkdir -p /etc/sudoers.d",
            f'echo "edward ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd',
            f"groupadd -g 1001 edward",
            f"useradd -m -u 1000 -d /home/edward -g 1001 -s /bin/sh edward"
        ]
    )
    dockerfile += docker.file.User(space=1, comment=["Switch to our user"], user="1000")
    dockerfile += docker.file.Run(
        space=1,
        comment=["Install golang"],
        commands=[
            "sudo chown edward:edward /home/edward",
            "sudo apt-get -y install curl wget git make tar",
            "sudo rm -rf /var/lib/apt/lists/*",
            "wget https://go.dev/dl/go1.20.14.linux-amd64.tar.gz -O ~/go-1.20.14.tar.gz",
            "sudo rm -rf /usr/local/go",
            "sudo tar -C /usr/local/ -xzf /home/edward/go-1.20.14.tar.gz",
            "sudo ln -s -f /usr/local/go/bin/go /usr/bin/go",
            "rm -rf /home/edward/go-1.20.14.tar.gz"
        ]
    )
    dockerfile += docker.file.Entrypoint(space=1, args=["sleep", "infinity"])

    remote = CustomContainer()
    remote.options.file = dockerfile
    remote.options.image.tag = "umk:0.2.0"
    remote.options.image.file = Path("/home/edward/astra/projects/umk/docker/Dockerfile")
    remote.options.container.name = "umk"
    remote.options.container.hostname = "unimake"
    remote.options.container.user = "1000"
    remote.options.container.workdir = Path("/home/edward/workdir")
    remote.options.container.entrypoint = ["sleep", "infinity"]
    remote.options.container.volumes.entries = [
        f"/home/edward/astra/projects/umk:/home/edward/workdir"
    ]

    remote.build()
    remote.up()
    remote.down()
    remote.destroy()
