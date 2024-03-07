import copy
import json
import os
from typing import Any

from umk import core, globals
from umk.framework.adapters.docker import options as opt
from umk.framework.adapters.docker import utils
from umk.framework.adapters.docker.models import Image, Container, Filter
from umk.framework.filesystem import Path
from umk.framework.system import Shell, ShellFetch


# ####################################################################################
# Base
# ####################################################################################


class BaseService(core.Object):
    shell: Shell = core.Field(
        default_factory=Shell
    )

    def run(self, cmd: list[str]) -> Shell:
        result = copy.deepcopy(self.shell)
        result.cmd += cmd
        return result


# ####################################################################################
# Images
# ####################################################################################


class ImageService(BaseService):
    def build(self, options: opt.ImageBuild):
        self.run(["build"] + options.serialize()).sync()

    def imports(self, options: opt.ImageImport):
        self.run(options.serialize()).sync()

    def load(self, file: Path) -> None | Image:
        if not file.parent.exists():
            os.makedirs(file.parent)
        shell = self.run(["load", "-q", "-i", file.as_posix()])
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None
        if not shell.handler.out:
            return None

        img = shell.handler.outstr().lstrip("Loaded image: ").strip()
        return self.get(img)

    def save(self, *images: str | Image, output: None | Path = None):
        entries = utils.entries(images)
        if not entries:
            return

        if not output.parent.exists():
            os.makedirs(output.parent)

        shell = self.run(["save", "-q", "-i"] + entries)
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None

    def ls(self, filters: Filter = None) -> list[Image]:
        shell = self.run(["ls", "-a", "--format", '{{.ID}}'])
        if filters:
            shell.cmd += ["--filter", str(filters)]
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return []
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return []
        if not shell.handler.out:
            return []

        result = []
        for img_id in shell.handler.out:
            if not img_id:
                continue
            img = self.inspect(img_id)
            if not img:
                continue
            result += img
        return result

    def prune(self, all=True, force=True, filters: Filter = None):
        shell = self.run(["prune"])
        if all:
            shell.cmd += ["--all"]
        if force:
            shell.cmd += ["--force"]
        if filters:
            shell.cmd += ["--filter", str(filters)]
        shell.sync()

    def pull(self, options: opt.ImagePull):
        self.run(options.serialize()).sync()

    def push(self, options: opt.ImagePush):
        self.run(options.serialize()).sync()

    def rm(self, *images: str | Image, force=True, no_prune=False):
        entries = utils.entries(images)
        if not entries:
            return

        shell = self.run(["rm"])
        if force:
            shell.cmd += ["--force"]
        if no_prune:
            shell.cmd += ["--no-prune"]
        shell.cmd += entries
        shell.sync()

    def tag(self, src: Image | str, dst: str) -> None | Image:
        img = src.id if issubclass(type(src), Image) else src
        shell = self.run(["tag", img, dst])
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None

        return self.get(dst)

    def inspect(self, image: str) -> None | Image:
        img = image.strip()
        if not img:
            return None

        shell = self.run(["inspect", "-f", "json", img])
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None

        try:
            details = json.loads(shell.handler.outstr())
            if isinstance(details, list):
                details = details[0]
            return Image(details=details)
        except Exception as e:
            globals.log.error(msg=str(e))
            return None

# ####################################################################################
# Remote environment utils implementation
# ####################################################################################


class ContainerService(BaseService):
    def attach(self, container: str, no_stdin=True, detach_keys: str = None):
        shell = self.run(["attach"])
        if no_stdin:
            shell.cmd.append("--no-stdin")
        if detach_keys:
            shell.cmd.append(f'--detach-keys="{detach_keys}"')
        shell.cmd.append(container)
        shell.sync()

    def commit(self, options: opt.ContainerCommit):
        self.run(options.serialize()).sync()

    def cp(self, src: Path, dst: Path, container: str | Container, to_host: bool, archive=False, follow_link=True):
        shell = self.run(["cp", "--quiet"])
        if archive:
            shell.cmd.append("--archive")
        if follow_link:
            self.shell.cmd.append("--follow-link")
        con = container.strip() if issubclass(type(container), str) else container.id
        if to_host:
            shell.cmd.append(f"{con}:{src}")
            shell.cmd.append(f"{dst}")
        else:
            shell.cmd.append(f"{src}")
            shell.cmd.append(f"{con}:{dst}")
        shell.sync()

    def create(self, options: opt.ContainerCreate) -> None | Container:
        shell = self.run(["create"])
        shell.cmd += options.serialize()
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None
        if not shell.handler.out:
            return None

        return self.inspect(shell.handler.out[-1])

    def diff(self, container: str | Container) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {
            "A": [],
            "C": [],
            "D": [],
        }

        entries = utils.entries(container)
        if not entries:
            return {}

        shell = self.run(["diff"] + entries)
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return result
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return result

        for line in shell.handler.out:
            line = line.strip()
            if not line:
                continue
            result[line[0]].append(line[2:])

        return result

    def exec(self, options: opt.ContainerExec):
        shell = self.run(["exec"])
        shell.cmd += options.serialize()
        shell.sync()

    def export(self, container: str | Container, output: Path):
        entries = utils.entries(container)
        if not entries:
            return
        shell = self.run(["export"])
        shell.cmd += ["--output", output.as_posix()]
        shell.cmd.extend(entries)
        shell.sync()

    def inspect(self, container: str) -> None | Container:
        entries = utils.entries(container)
        if not entries:
            return

        shell = self.run(["inspect", "-f", "json"] + entries)
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return None
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return None

        try:
            details = json.loads(shell.handler.outstr())
            if isinstance(details, list):
                details = details[0]
            return Container(details=details)
        except Exception as e:
            globals.log.error(msg=str(e))
            return None

    def kill(self, *containers: str | Container, signal: int):
        entries = utils.entries(containers)
        if not entries:
            return None
        shell = self.run(["kill", "--signal", str(signal)] + entries)
        shell.sync()

    def ls(self, filters: Filter = None) -> list[Container]:
        shell = self.run(["ls", "-a", "--format", '{{.ID}}'])
        if filters:
            shell.cmd += ["--filter", str(filters)]
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return []
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return []
        if not shell.handler.out:
            return []

        result = []
        for con_id in shell.handler.out:
            if not con_id:
                continue
            container = self.inspect(con_id)
            if not container:
                continue
            result += container
        return result

    def pause(self, *containers: str | Container):
        entries = utils.entries(containers)
        if not entries:
            return None
        shell = self.run(["pause"] + entries)
        shell.sync()

    def port(self, container: str | Container, port: int = None, protocol: str = None) -> dict[str, str]:
        entries = utils.entries(container)
        if not entries:
            return {}
        shell = self.run(["port"] + entries)
        if port and protocol:
            shell.cmd.append(f"{str(port)}/{protocol}")
        elif port:
            shell.cmd.append(str(port))
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return {}
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return {}
        if not shell.handler.out:
            return {}

        result = {}
        for entry in shell.handler.out:
            if "->" in entry:
                split = entry.split("->")
                k = split[0]
                v = split[1]
                result[k] = v
            else:
                k = str(port)
                if protocol:
                    k += "/" + protocol
                result[k] = entry

        return result

    def prune(self, force=True, filters: Filter = None):
        shell = self.run(["prune"])
        if force:
            shell.cmd += ["--force"]
        if filters:
            shell.cmd += ["--filter", str(filters)]
        shell.sync()

    def rename(self, container: str | Container, name: str):
        entry = utils.entries(container)
        if not entry:
            return
        shell = self.run(["rename"])
        shell.cmd.extend(entry)
        shell.cmd.append(name)
        shell.sync()

    def restart(self, *containers: str | Container, signal: int = None, time: int = None):
        entries = utils.entries(containers)
        if not entries:
            return
        shell = self.run(["restart"])
        if signal:
            shell.cmd += ["--signal", signal]
        if time:
            shell.cmd += ["--time", time]
        shell.cmd += entries
        shell.sync()

    def rm(self, container: str | Container, force=False, link=False, volumes=False):
        entries = utils.entries(container)
        if not entries:
            return
        shell = self.run(["rm"])
        if force:
            shell.cmd += ["--force"]
        if link:
            shell.cmd += ["--link"]
        if volumes:
            shell.cmd += ["--volumes"]
        shell.cmd.extend(entries)
        shell.sync()

    def start(self, container: str | Container, attach=False, interactive=False, detach_keys: None | str = None):
        entries = utils.entries(container)
        if not entries:
            return
        shell = self.run(["start"])
        if attach:
            shell.cmd += ["--attach"]
        if interactive:
            shell.cmd += ["--interactive"]
        if detach_keys:
            shell.cmd += ["--detach-keys", detach_keys]
        shell.cmd.extend(entries)
        shell.sync()

    def stats(self, container: str | Container) -> dict[str, Any]:
        entries = utils.entries(container)
        if not entries:
            return {}
        shell = self.run(["stats", "--no-stream", "--format", "json"] + entries)
        shell.handler = ShellFetch()
        shell.sync()

        if shell.handler.exc:
            globals.log.error(msg=str(shell.handler.exc))
            return {}
        if shell.handler.err:
            globals.log.error(msg=shell.handler.errstr())
            return {}

        try:
            return json.loads(shell.handler.outstr())
        except Exception as e:
            globals.log.error(msg=str(e))
            return {}

    def stop(self, container: str | Container, signal: int, time: None | int = None):
        entries = utils.entries(container)
        if not entries:
            return
        shell = self.run(["stop"])
        shell.cmd += ["--signal", str(signal)]
        if time:
            shell.cmd += ["--time", str(time)]
        shell.cmd.extend(entries)
        shell.sync()

    def unpause(self, *containers: str | Container):
        entries = utils.entries(containers)
        if not entries:
            return
        shell = self.run(["unpause"] + entries)
        shell.sync()

    def update(self, options: opt.ContainerUpdate):
        shell = self.run(["update"] + options.serialize())
        shell.sync()

    def wait(self, *containers: str | Container):
        entries = utils.entries(containers)
        if not entries:
            return
        shell = self.run(["wait"] + entries)
        shell.sync()


# ####################################################################################
# Client
# ####################################################################################


class Client(core.Object):
    images: ImageService = core.Field(
        default_factory=ImageService,
        description="Docker image service. It implements 'docker image *' commands."
    )
    containers: ContainerService = core.Field(
        default_factory=ContainerService,
        description="Docker container service. It implements 'docker container' commands."
    )


def client(config: opt.ClientConfig = None, cmd: list[str] = None, log=True, title="docker") -> Client:
    entry = cmd if cmd else ["docker"]
    if config:
        entry += config.serialize()

    shell = Shell(
        name=title,
        cmd=entry,
        log=log
    )

    result = Client()
    result.images.shell = copy.deepcopy(shell)
    result.images.shell.cmd.extend(["image"])
    result.containers.shell = copy.deepcopy(shell)
    result.containers.shell.cmd.extend(["container"])

    return result


if __name__ == '__main__':
    from umk.framework.adapters import docker

    dfp = Path("/home/edward/astra/projects/umk/docker/Dockerfile")
    dfo = docker.File()
    dfo += docker.file.From(
        comment=["Base on astralinux"],
        image="ubuntu:latest"
    )
    dfo += docker.file.Label(
        space=1,
        comment=["Add some labels"],
        items={"hello": "world"}
    )
    dfo += docker.file.Run(
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
    dfo += docker.file.User(space=1, comment=["Switch to our user"], user="1000")
    dfo += docker.file.Run(
        space=1,
        comment=["Install golang"],
        commands=[
            "sudo chown edward:edward /home/edward",
            "sudo apt-get -y install python3"
        ]
    )
    dfo += docker.file.Run(
        space=1,
        comment=["Generate python script"],
        commands=[
            "cd /home/edward",
            'echo "import time" >> app.py',
            'echo "while True:" >> app.py',
            'echo "\tprint(\\"hello world\\")" >> app.py',
            'echo "\ttime.sleep(1)" >> app.py',
            'echo "\\n" >> app.py',
        ]
    )
    dfo += docker.file.Workdir(space=1, path="/home/edward")
    dfo += docker.file.Entrypoint(space=1, args=["sleep", "infinity"])
    # dfo += docker.file.Entrypoint(space=1, args=["python", "app.py"])
    dfo.save(dfp)

    cli = client(log=True)

    # clean
    cli.containers.stop("unimake", signal=9)
    cli.containers.rm("unimake", force=True)
    cli.images.rm("unimake", force=True)

    # build dockerfile
    cli.images.build(
        options=opt.ImageBuild(
            path=dfp.parent,
            tag=["unimake"]
        )
    )
    img = cli.images.inspect("unimake")

    # create container
    con = cli.containers.create(
        options=opt.ContainerCreate(
            name="unimake",
            workdir="/home/edward",
            user="1000:1001",
            image=img.tags[0]
        )
    )

    # start container
    cli.containers.start(con)

    # # create file in the container
    # cli.containers.exec(
    #     options=opt.ContainerExec(
    #         container=con.id,
    #         cmd=["echo", '"some"', ">", "hello.txt"],
    #         workdir="/home/edward",
    #         user="edward"
    #     )
    # )

    print(cli.containers.export("unimake", output=Path("/home/edward/astra/projects/umk/umk.tar")))

    # attach to container
    # cli.containers.attach("35e704e206db")
