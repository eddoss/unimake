import logging
import os

import paramiko
from paramiko import util as paramiko_util

from umk import core
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface
from umk.framework.system.environs import Environs
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

    def client(self) -> paramiko.SSHClient:
        paramiko_util.get_logger('paramiko').setLevel(logging.ERROR)
        result = paramiko.SSHClient()
        result.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result.connect(self.host, self.port, self.username, self.password)
        return result

    def shell(self, **kwargs):
        paramiko_util.get_logger('paramiko').setLevel(logging.ERROR)
        cmd = ["ssh", f"{self.username}@{self.host}", "-p", str(self.port)]
        if self.sh:
            cmd.extend(["-t", self.sh.strip()])
        Shell(name=self.name, cmd=cmd).sync()

    @core.typeguard
    def execute(self, cmd: list[str], cwd: None | Path | str = None, env: None | Environs = None, **kwargs):
        paramiko_util.get_logger('paramiko').setLevel(logging.ERROR)
        client = self.client()
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
    def upload(self, paths: dict[str | Path, str | Path], **kwargs):
        if not paths:
            return
        client = self.client()
        with client.open_sftp() as transport:
            for src, dst in paths.items():
                core.globals.console.print(f"[bold]\[{self.name}] upload: {src} -> {dst}")
                transport.put(
                    localpath=str(Path(src).expanduser().resolve().absolute()),
                    remotepath=str(dst)
                )
        client.close()

    @core.typeguard
    def download(self, items: dict[str | Path, str | Path], **kwargs):
        if not items:
            return
        client = self.client()
        with client.open_sftp() as transport:
            for src, dst in items.items():
                core.globals.console.print(f"[bold]\[{self.name}] download: {src} -> {dst}")
                dst = Path(dst).expanduser().resolve().absolute()
                if not dst.parent.exists():
                    os.makedirs(dst.parent)
                transport.get(
                    remotepath=str(src),
                    localpath=str(dst)
                )
        client.close()
