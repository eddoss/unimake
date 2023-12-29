import umk
from umk.framework import cli
from umk.framework.adapters import docker


@cli.cmd()
def build():
    client = docker.client()
    repo = "dev.unimake.base"
    try:
        client.images.remove("latest")
    except Exception as e:
        umk.print(e)
