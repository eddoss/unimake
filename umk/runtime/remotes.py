from umk import framework, core
from umk.core.typings import Generator
from umk.runtime import utils


class Remote(core.Model):
    class Decorators(core.Model):
        custom: utils.Decorator = core.Field(
            description="Decorator of the remote 'custom'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                module="remotes",
                input=utils.Decorator.Input(
                    subject="class",
                    base=framework.remote.Interface,
                ),
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register custom remote environment outside of the .unimake/remote.py"),
                    subject=utils.ClassError("Failed to register custom remote environment. Use 'umk.framework.remote.custom' with classes based on 'umk.framework.remote.Interface'"),
                    base=utils.SubclassError("Failed to register custom remote environment. Use 'umk.framework.remote.custom' with classes based on 'umk.framework.remote.Interface'"),
                )
            )
        )
        ssh: utils.Decorator = core.Field(
            description="Decorator of the remote 'ssh'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="remotes",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'ssh' outside of the .unimake/remotes.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'ssh'. Use 'umk.framework.remotes.ssh with functions"),
                    sig=utils.SignatureError("Failed to register remote environment 'ssh'. Function must accept 1 argument at least"),
                )
            ),
        )
        container: utils.Decorator = core.Field(
            description="Decorator of the remote 'docker.container'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="remotes",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'docker.container' outside of the .unimake/remotes.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'docker.container'. Use 'umk.framework.remotes.docker.container with functions"),
                    sig=utils.SignatureError("Failed to register remote environment 'docker.container'. Function must accept 1 argument at least"),
                )
            ),
        )
        compose: utils.Decorator = core.Field(
            description="Decorator of the remote 'docker.compose'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="remotes",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'docker.compose' outside of the .unimake/remotes.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'docker.compose'. Use 'umk.framework.remotes.docker.compose with functions"),
                    sig=utils.SignatureError("Failed to register remote environment 'docker.compose'. Function must accept 1 argument at least"),
                )
            ),
        )
    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Targets decorators"
    )
    items: dict[str, framework.remote.Interface] = core.Field(
        default_factory=dict,
        description="List of the remote environments"
    )
    default: str = core.Field(
        default="",
        description="Default remote environment name"
    )

    def __iter__(self):
        for rem in self.items.values():
            yield rem

    def __getitem__(self, name: str):
        return self.items[name]

    def __len__(self):
        return len(self.items)

    def __contains__(self, name: str):
        return name in self.items

    def get(self, name: str, on_err=None) -> framework.remote.Interface:
        return self.items.get(name, on_err)

    def find(self, name: str, on_err=None) -> None | framework.remote.Interface:
        return self.get(name, on_err)

    def init(self):
        framework.remote.iterate = self.__iter__
        framework.remote.find = self.find
        framework.remote.default = lambda on_err=None: self.get(self.default, on_err)
        framework.remote.ssh = self.decorator.ssh.register
        framework.remote.docker.container = self.decorator.container.register
        framework.remote.docker.compose = self.decorator.compose.register
        framework.remote.custom = self.decorator.custom.register

    def setup(self, c: framework.config.Interface, p: framework.project.Interface):
        def append(r: framework.remote.Interface):
            if r.name in self.items:
                e = utils.ExistsError()
                e.messages.append(f"Remote environment '{r.name}' is already registered")
                e.details.new(name="name", value=r.name, desc="Remote environment name")
                raise e
            if r.default:
                if self.default:
                    e = utils.ExistsError()
                    e.messages = f"Remote environment '{r.name}' is marked as default, but default is already exists: '{self.default}'"
                    raise e
                self.default = r.name
            self.items[r.name] = r
        for defer in self.decorator.compose.defers:
            rem = framework.remote.DockerCompose()
            sig = self.decorator.compose.input.sig
            defer(sig.min, sig.max, rem, c, p)
            append(rem)
        for defer in self.decorator.container.defers:
            rem = framework.remote.DockerContainer()
            sig = self.decorator.container.input.sig
            defer(sig.min, sig.max, rem, c, p)
            append(rem)
        for defer in self.decorator.ssh.defers:
            rem = framework.remote.SecureShell()
            sig = self.decorator.ssh.input.sig
            defer(sig.min, sig.max, rem, c, p)
            append(rem)
        for defer in self.decorator.custom.defers:
            rem = defer(0, 2, c, p)
            append(rem)
