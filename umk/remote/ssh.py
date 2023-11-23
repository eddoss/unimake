import logging
import os
import paramiko
from pathlib import Path
from beartype import beartype
from beartype.typing import Optional
from umk.globals import Global
from umk.remote.interface import Interface, Property
from umk.system.environs import OptEnv
from umk.system.shell import Shell
from paramiko import util as paramiko_util


class Ssh(Interface):
    @property
    def host(self) -> str:
        return self._host

    @host.setter
    @beartype
    def host(self, value: str):
        self._host = value
        self._details["host"].value = self._host

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    @beartype
    def port(self, value: int):
        self._port = value
        self._details["port"].value = self._port

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    @beartype
    def password(self, value: str):
        self._password = value
        self._details["pass"].value = self._password

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    @beartype
    def username(self, value: str):
        self._username = value
        self._details["user"].value = self._username

    @property
    def sh(self) -> Optional[str]:
        return self._sh

    @sh.setter
    @beartype
    def sh(self, value: Optional[str]):
        self._sh = value
        self._details["shell"].value = self._sh

    @beartype
    def __init__(
        self,
        name: str = "",
        description: str = "Secure shell",
        default: bool = False,
        host: str = "",
        username: str = "",
        password: str = "",
        port: int = 22,
        shell: Optional[str] = None
    ):
        super().__init__(name=name, description=description, default=default)

        paramiko_util.get_logger('paramiko').setLevel(logging.ERROR)

        self._host = host
        self._port = port
        self._password = password
        self._username = username
        self._sh = shell

        self._details['host'] = Property('host', 'Remote server address', self.host)
        self._details['port'] = Property('port', 'Remote server port (default is 22)', self.port)
        self._details['user'] = Property('user', 'User login', self.username)
        self._details['pass'] = Property('pass', 'User password', self.password)
        self._details['shell'] = Property('shell', 'Default shell', self.sh)

    def shell(self, *args, **kwargs):
        cmd = ["ssh", f"{self.username}@{self.host}", "-p", str(self.port)]
        if self.sh:
            cmd.extend(["-t", self.sh.strip()])
        Shell(name=self.name, command=cmd).sync()

    def execute(self, cmd: list[str], cwd: str = '', env: OptEnv = None, *args, **kwargs):
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

    @beartype
    def upload(self, paths: dict[str, str], *args, **kwargs):
        if not paths:
            return
        client = self._client()
        with client.open_sftp() as transport:
            for src, dst in paths.items():
                Global.console.print(f"[bold]\[{self.name}] upload: {src} -> {dst}")
                transport.put(
                    localpath=Path(src).expanduser().resolve().absolute().as_posix(),
                    remotepath=dst
                )
        client.close()

    @beartype
    def download(self, paths: dict[str, str], *args, **kwargs):
        if not paths:
            return
        client = self._client()
        with client.open_sftp() as transport:
            for src, dst in paths.items():
                Global.console.print(f"[bold]\[{self.name}] download: {src} -> {dst}")
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

# class Sftp(Transport):
#     @property
#     def client(self) -> paramiko.SSHClient:
#         return self._client
#
#     @beartype
#     def __init__(self, host: str, username: str, password: str, port: int = 22):
#         self._host = host
#         self._port = port
#         self._password = password
#         self._username = username
#         self._client = paramiko.SSHClient()
#
#     def open(self, *args, **kwargs):
#         self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         self._client.connect(self.host, self.port, self.username, self.password)
#
#     def close(self, *args, **kwargs):
#         self._client.close()
#
#     def bytes(self, src: bytes, dst: Path):
#         pass
#
#     def text(self, src: str, dst: Path):
#         pass
#
#     def file(self, src: str, dst: Path):
#         pass
