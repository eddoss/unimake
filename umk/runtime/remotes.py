from collections import OrderedDict

from umk import core
from umk.kit import project, config, remote
from umk.runtime import utils


class Remote(core.Model):
    class Decorators(core.Model):
        custom: utils.Decorator = core.Field(
            description="Decorator of the remote 'custom'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                module="remote",
                input=utils.Decorator.Input(
                    subject="class",
                    base=remote.Interface,
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
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Secure shell instance"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="remote",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'ssh' outside of the .unimake/remote.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'ssh'. Use 'umk.framework.remote.ssh with functions"),
                )
            ),
        )
        container: utils.Decorator = core.Field(
            description="Decorator of the remote 'docker.container'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Secure shell instance"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="remote",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'docker.container' outside of the .unimake/remote.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'docker.container'. Use 'umk.framework.remote.docker.container with functions"),
                )
            ),
        )
        compose: utils.Decorator = core.Field(
            description="Decorator of the remote 'docker.compose'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Secure shell instance"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="remote",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register remote environment 'docker.compose' outside of the .unimake/remote.py"),
                    subject=utils.FunctionError("Failed to register remote environment 'docker.compose'. Use 'umk.framework.remote.docker.compose with functions"),
                )
            ),
        )
    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Targets decorators"
    )
    items: dict[str, remote.Interface] = core.Field(
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

    def get(self, name: str, on_err=None) -> remote.Interface:
        return self.items.get(name, on_err)

    def find(self, name: str, on_err=None) -> remote.Interface | None:
        return self.get(name, on_err)

    def init(self):
        remote.iterate = self.__iter__
        remote.find = self.find
        remote.default = lambda on_err=None: self.get(self.default, on_err)
        remote.ssh = self.decorator.ssh.register
        remote.docker.container = self.decorator.container.register
        remote.docker.compose = self.decorator.compose.register
        remote.custom = self.decorator.custom.register

    def setup(self, c: config.Interface, p: project.Interface):
        def append(r: remote.Interface):
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
            args = {"s": remote.DockerCompose(), "c": c, "p": p}
            self.decorator.compose.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.container.defers:
            args = {"s": remote.DockerContainer(), "c": c, "p": p}
            self.decorator.container.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.ssh.defers:
            args = {"s": remote.SecureShell(), "c": c, "p": p}
            self.decorator.ssh.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.custom.defers:
            args = {"c": c, "p": p}
            res = self.decorator.custom.sig.call(defer.func, args)
            append(res)

        self.decorator.custom.skip = True
        self.decorator.ssh.skip = True
        self.decorator.compose.skip = True
        self.decorator.container.skip = True
