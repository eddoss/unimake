import logging
import os

import paramiko
from paramiko import util as paramiko_util

from umk import globals, core
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell


class SecureShell(Interface):
    host: str = core.Field(
        default="",
        description="Remote server IP address"
    )
    port: int = core.Field(
        default=22,
        description="Remote server port"
    )
    password: str = core.Field(
        default="",
        description="Remote server user password"
    )
    username: str = core.Field(
        default="",
        description="Remote server user name"
    )
    sh: str = core.Field(
        default="",
        description="Default shell (bash, sh, zsh ...)"
    )

    @core.typeguard
    def __init__(
        self,
        name: str = "",
        description: str = "Secure shell",
        default: bool = False,
        host: str = "",
        username: str = "",
        password: str = "",
        port: int = 22,
        shell: str | None = None
    ):
        super().__init__(
            name=name, 
            description=description, 
            default=default,
        )

        paramiko_util.get_logger('paramiko').setLevel(logging.ERROR)

        self.host = host
        self.port = port
        self.password = password
        self.username = username
        self.sh = shell

    def shell(self, **kwargs):
        cmd = ["ssh", f"{self.username}@{self.host}", "-p", str(self.port)]
        if self.sh:
            cmd.extend(["-t", self.sh.strip()])
        Shell(name=self.name, command=cmd).sync()

    @core.typeguard
    def execute(self, cmd: list[str], cwd: str = '', env: envs.Optional = None, **kwargs):
        client = self._client()
        _, out, err = client.exec_command(
            command=Shell.stringify(cmd),
            environment=None,
            get_pty=True
        )
        for line in out:
            print(line.rstrip())
        for line in err:
            print(line.rstrip())

    @core.typeguard
    def upload(self, paths: dict[str, str], **kwargs):
        if not paths:
            return
        client = self._client()
        with client.open_sftp() as transport:
            for src, dst in paths.items():
                globals.console.print(f"[bold]\[{self.name}] upload: {src} -> {dst}")
                transport.put(
                    localpath=Path(src).expanduser().resolve().absolute().as_posix(),
                    remotepath=dst
                )
        client.close()

    @core.typeguard
    def download(self, items: dict[str, str], **kwargs):
        if not items:
            return
        client = self._client()
        with client.open_sftp() as transport:
            for src, dst in items.items():
                globals.console.print(f"[bold]\[{self.name}] download: {src} -> {dst}")
                dst = Path(dst).expanduser().resolve().absolute()
                if not dst.parent.exists():
                    os.makedirs(dst.parent)
                transport.get(
                    remotepath=src,
                    localpath=dst.as_posix()
                )
        client.close()

    def _client(self):
        result = paramiko.SSHClient()
        result.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result.connect(self.host, self.port, self.username, self.password)
        return result

    def _register_properties(self):
        super()._register_properties()
        self._properties.add("host")
        self._properties.add("port")
        self._properties.add("username")
        self._properties.add("password")
        self._properties.add("sh")
