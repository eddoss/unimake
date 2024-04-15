from umk import framework, core
from umk.core.typings import Generator
from umk.runtime import utils


class Targets(core.Model):
    class Decorators(core.Model):
        custom: utils.Decorator = core.Field(
            description="Decorator of the target 'custom'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                module="targets",
                input=utils.Decorator.Input(
                    subject="class",
                    base=framework.target.Interface,
                ),
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register custom target outside of the .unimake/targets.py"),
                    subject=utils.ClassError("Failed to register custom target. Use 'umk.framework.targets.custom' with classes based on 'umk.framework.targets.Interface'"),
                    base=utils.SubclassError("Failed to register custom target. Use 'umk.framework.targets.custom' with classes based on 'umk.framework.targets.Interface'"),
                )
            )
        )
        function: utils.Decorator = core.Field(
            description="Decorator of the target 'function'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                module="targets",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'function' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'function'. Use 'umk.framework.targets.function' with functions")
                )
            ),
        )
        go_binary: utils.Decorator = core.Field(
            description="Decorator of the target 'go.binary'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="targets",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'go.binary' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'go.binary'. Use 'umk.framework.targets.go.binary' with functions"),
                    sig=utils.SignatureError("Failed to register target 'go.binary'. Function must accept 1 argument at least"),
                )
            ),
        )
        command: utils.Decorator = core.Field(
            description="Decorator of the target 'command'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="targets",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'command' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'command'. Use 'umk.framework.targets.go.binary' with functions"),
                    sig=utils.SignatureError("Failed to register target 'command'. Function must accept 1 argument at least"),
                )
            ),
        )
        packages: utils.Decorator = core.Field(
            description="Decorator of the target 'packages'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                    sig=utils.Decorator.Input.Signature(min=1)
                ),
                module="targets",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'packages' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError(
                        "Failed to register target 'command'. Use 'umk.framework.targets.packages' with functions"),
                    sig=utils.SignatureError(
                        "Failed to register target 'packages'. Function must accept 1 argument at least"),
                )
            ),
        )
    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Targets decorators"
    )
    items: dict[str, framework.target.Interface] = core.Field(
        default_factory=dict,
        description="Project targets"
    )

    def __iter__(self):
        for t in self.items.values():
            yield t

    def __contains__(self, name: str):
        return name in self.items

    def objects(self) -> Generator[framework.target.Interface, None, None]:
        for item in self.items.values():
            yield item.object()

    def get(self, name: str, on_err=None) -> framework.target.Interface:
        return self.items.get(name, on_err)

    def run(self, *names: str):
        found = []
        for name in names:
            if name not in self.items:
                core.globals.console.print(f"[yellow bold]Target '{name}' not found")
            else:
                found.append(name)
        for name in found:
            target = self.get(name)
            target.run(p=framework.project.get(), c=framework.config.get())

    def init(self):
        framework.target.run = self.run
        framework.target.function = self.decorator.function.register
        framework.target.custom = self.decorator.custom.register
        framework.target.command = self.decorator.command.register
        framework.target.packages = self.decorator.packages.register
        framework.target.go.binary = self.decorator.go_binary.register

    def setup(self, c: framework.config.Interface, p: framework.project.Interface):
        def append(t: framework.target.Interface):
            if t.name in self.items:
                e = utils.ExistsError()
                e.messages.append(f"Target '{t.name}' is already registered")
                e.details.new(name="name", value=t.name, desc="Target name")
                raise e
            self.items[t.name] = t

        for defer in self.decorator.function.defers:
            target = framework.target.Function(
                name=defer.args.get("name", defer.func.__name__),
                description=defer.args.get("description", (defer.func.__doc__ or "").strip()),
                label=defer.args.get("label", ""),
                function=defer.func
            )
            append(target)
        for defer in self.decorator.go_binary.defers:
            target = framework.target.GolangBinary()
            sig = self.decorator.go_binary.input.sig
            with_debug = defer.args.get("debug", True)
            defer(sig.min, sig.max, target, c, p)
            if with_debug:
                d, r = framework.target.GolangBinary.new(
                    name=target.name,
                    label=target.label,
                    description=target.description,
                    tool=target.tool,
                    build=target.build,
                    port=target.debug.port,
                )
                append(d)
                append(r)
            else:
                append(target)
        for defer in self.decorator.command.defers:
            target = framework.target.Command()
            sig = self.decorator.go_binary.input.sig
            defer(sig.min, sig.max, target, c, p)
            append(target)
        for defer in self.decorator.packages.defers:
            target = framework.target.SystemPackages()
            sig = self.decorator.packages.input.sig
            defer(sig.min, sig.max, target, c, p)
            append(target)
        for defer in self.decorator.custom.defers:
            target = defer(0, 2, c, p)
            append(target)
