from collections import OrderedDict

from umk import core
from umk.kit import config, target, project
from umk.core.typings import Generator
from umk.runtime import utils


class Targets(core.Model):
    class Decorators(core.Model):
        custom: utils.Decorator = core.Field(
            description="Decorator of the target 'custom'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                module="project",
                input=utils.Decorator.Input(
                    subject="class",
                    base=target.Interface,
                ),
                sig=utils.Signature(
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
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
                sig=utils.Signature(
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    },
                ),
                module="project",
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
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Object to build"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="project",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'go.binary' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'go.binary'. Use 'umk.framework.targets.go.binary' with functions"),
                )
            ),
        )
        go_mod: utils.Decorator = core.Field(
            description="Decorator of the target 'go.mod'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Object to build"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="project",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'go.mod' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'go.mod'. Use 'umk.framework.targets.go.binary' with functions"),
                )
            ),
        )
        command: utils.Decorator = core.Field(
            description="Decorator of the target 'command'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Object to build"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="project",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'command' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError("Failed to register target 'command'. Use 'umk.framework.targets.go.binary' with functions"),
                )
            ),
        )
        packages: utils.Decorator = core.Field(
            description="Decorator of the target 'packages'",
            default_factory=lambda: utils.Decorator(
                stack=2,
                input=utils.Decorator.Input(
                    subject="function",
                ),
                sig=utils.Signature(
                    required=OrderedDict({
                        "s": utils.SignatureArgument(description="Object to build"),
                    }),
                    optional={
                        "c": utils.SignatureArgument(description="Config instance"),
                        "p": utils.SignatureArgument(description="Project instance"),
                    }
                ),
                module="project",
                errors=utils.Decorator.OnErrors(
                    module=utils.SourceError("Failed to register target 'packages' outside of the .unimake/targets.py"),
                    subject=utils.FunctionError(
                        "Failed to register target 'command'. Use 'umk.framework.targets.packages' with functions"),
                )
            ),
        )
    decorator: Decorators = core.Field(
        default_factory=Decorators,
        description="Targets decorators"
    )
    items: dict[str, target.Interface] = core.Field(
        default_factory=dict,
        description="Project targets"
    )

    def __iter__(self):
        for t in self.items.values():
            yield t

    def __contains__(self, name: str):
        return name in self.items

    def objects(self) -> Generator[target.Interface, None, None]:
        for item in self.items.values():
            yield item.object()

    def get(self, name: str, on_err=None) -> target.Interface:
        return self.items.get(name, on_err)

    def run(self, *names: str):
        found = []
        for name in names:
            if name not in self.items:
                core.globals.console.print(f"[yellow bold]Target '{name}' not found")
            else:
                found.append(name)
        for name in found:
            t = self.get(name)
            t.run()

    def init(self):
        target.run = self.run
        target.function = self.decorator.function.register
        target.custom = self.decorator.custom.register
        target.command = self.decorator.command.register
        target.packages = self.decorator.packages.register
        target.go.binary = self.decorator.go_binary.register
        target.go.mod = self.decorator.go_mod.register

    def setup(self, c: config.Interface, p: project.Interface):
        def append(tar: target.Interface):
            if tar.name in self.items:
                e = utils.ExistsError()
                e.messages.append(f"Target '{tar.name}' is already registered")
                e.details.new(name="name", value=tar.name, desc="Target name")
                raise e
            self.items[tar.name] = tar

        for defer in self.decorator.function.defers:
            t = target.Function(
                name=defer.args.get("name", defer.func.__name__),
                description=defer.args.get("description", (defer.func.__doc__ or "").strip()),
                label=defer.args.get("label", ""),
                function=lambda: self.decorator.function.sig.call(defer.func, {"c": c, "p": p})
            )
            append(t)
        for defer in self.decorator.go_binary.defers:
            args = {"s": target.GolangBinary(), "c": c, "p": p}
            self.decorator.go_binary.sig.call(defer.func, args)
            with_debug = defer.args.get("debug", True)
            if with_debug:
                d, r = target.GolangBinary.new(
                    name=args["s"].name,
                    label=args["s"].label,
                    description=args["s"].description,
                    tool=args["s"].tool,
                    build=args["s"].build,
                    port=args["s"].debug.port,
                )
                append(d)
                append(r)
            else:
                append(args["s"])
        for defer in self.decorator.command.defers:
            args = {"s": target.Command(), "c": c, "p": p}
            self.decorator.command.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.go_mod.defers:
            args = {"s": target.GolangMod(), "c": c, "p": p}
            self.decorator.go_mod.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.packages.defers:
            args = {"s": target.SystemPackages(), "c": c, "p": p}
            self.decorator.packages.sig.call(defer.func, args)
            append(args["s"])
        for defer in self.decorator.custom.defers:
            args = {"c": c, "p": p}
            res = self.decorator.custom.sig.call(defer.func, args)
            append(res)

        self.decorator.custom.skip = True
        self.decorator.go_mod.skip = True
        self.decorator.go_binary.skip = True
        self.decorator.function.skip = True
        self.decorator.command.skip = True
        self.decorator.packages.skip = True
