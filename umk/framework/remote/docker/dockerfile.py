from umk import core, globals
from umk.framework.filesystem import Path
from umk.framework.remote.docker.container import Container
from umk.framework.remote.interface import Events
from umk.framework.adapters.docker import file as dockerfile
from umk.framework.adapters.docker import client as docker_client
from umk.framework.adapters.docker.types import ContainerCreateOptions, ImageBuildOptions


class File(Container):
    file: dockerfile.File = core.Field(
        default_factory=dockerfile.File,
        description="Dockerfile object"
    )
    container: ContainerCreateOptions = core.Field(
        default_factory=ContainerCreateOptions,
        description="Container create options"
    )
    image: ImageBuildOptions = core.Field(
        default_factory=ImageBuildOptions,
        description="Image build options"
    )

    def build(self, **kwargs):
        ed = core.EventData()
        ed.new("path", self.path, "Dockerfile output path")
        ed.new("container", self.path, "Docker container name")
        ed.new("image", self.path, "Docker image name")
        ed.new("file", self.path, "Dockerfile object")
        globals.events.dispatch(
            Events.build(before=True, instance=self, data=ed)
        )
        try:
            client = docker_client()
            client.images.build(**self.image.to_native_params())
            client.containers.create(self.container.image, **self.container.to_native_params())
        except Exception as err:
            globals.log.fatal(msg=f"[remotes] name={self.name} error={err}")
            globals.close(-1)

    def destroy(self, **kwargs):
        super().destroy(**kwargs)

    def up(self, **kwargs):
        super().up(**kwargs)

    def down(self, **kwargs):
        super().down(**kwargs)

    def build_image(self):
        try:
            client.images.build(**self.image.to_native_params())
        except Exception as err:


    def build_container(self):
        client = docker_client()
        client.containers.create()