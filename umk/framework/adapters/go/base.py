import copy

from umk import core
from umk.framework.utils import cli
from umk.framework.filesystem import Path, AnyPath
from umk.framework.system.shell import Shell


class BuildOptions(cli.Options):
    @staticmethod
    def new(mode: str, output: AnyPath, *sources: AnyPath) -> 'BuildOptions':
        match mode:
            case "release":
                return BuildOptions.release(output, *sources)
            case "debug":
                return BuildOptions.debug(output, *sources)
        raise ValueError(f"Invalid mode for golang build options: given={mode}, expect=[release, debug]")

    @staticmethod
    def release(output: AnyPath, *sources: AnyPath) -> 'BuildOptions':
        result = BuildOptions()
        result.output = output
        result.flags.gc.append('-dwarf=false')
        result.flags.ld.append('-s')
        result.flags.ld.append('-w')
        if sources:
            result.source = sources
        return result

    @staticmethod
    def debug(output: AnyPath, *sources: AnyPath) -> 'BuildOptions':
        result = BuildOptions()
        result.output = output
        result.flags.gc.append('all=-N')
        result.flags.gc.append('-l')
        if sources:
            result.source = sources
        return result

    class Print(cli.Options):
        packages: bool = core.Field(
            default=False,
            cli=cli.Bool(name="-v"),
            description="Print the names of packages as they are compiled."
        )
        commands: bool = core.Field(
            default=False,
            cli=cli.Bool(name="-x"),
            description="Print the commands."
        )

    class Cover(cli.Options):
        enabled: None | bool = core.Field(
            default=None,
            cli=cli.Bool(name="-cover"),
            description="Enable code coverage instrumentation."
        )
        mode: None | str = core.Field(
            default=None,
            cli=cli.Str(name="-covermode"),
            description="Set the mode for coverage analysis.the default is 'set' unless -race is enabled,in which case it is 'atomic'.the values:set: bool: does this statement run?count: int: how many times does this statement run?atomic: int: count, but correct in multithreaded tests;significantly more expensive.sets -cover."
        )
        pkg: list[str] = core.Field(
            default_factory=list,
            cli=cli.List(name="-coverpkg"),
            description="For a build that targets package 'main' (e.g. building a goexecutable), apply coverage analysis to each package matchingthe patterns. the default is to apply coverage analysis topackages in the main go module. see 'go help packages' for adescription of package patterns.  sets -cover."
        )

    class Profiling(cli.Options):
        race: None | bool = core.Field(
            default=None,
            cli=cli.Bool(name="-race"),
            description="Enable data race detection.supported only on linux/amd64, freebsd/amd64, darwin/amd64, darwin/arm64, windows/amd64,linux/ppc64le and linux/arm64 (only for 48-bit vma)."
        )
        memory: None | bool = core.Field(
            default=None,
            cli=cli.Bool(name="-msan"),
            description="Enable interoperation with memory sanitizer.supported only on linux/amd64, linux/arm64, freebsd/amd64and only with clang/llvm as the host c compiler.pie build mode will be used on all platforms except linux/amd64."
        )
        address: None | bool = core.Field(
            default=None,
            cli=cli.Bool(name="-asan"),
            description="Enable interoperation with address sanitizer.supported only on linux/arm64, linux/amd64.supported only on linux/amd64 or linux/arm64 and only with gcc 7 and higheror clang/llvm 9 and higher."
        )

    class Mod(cli.Options):
        strategy: None | str = core.Field(
            default=None,
            cli=cli.Str(name="-mod"),
            description="Module download mode to use: readonly, vendor, or mod.by default, if a vendor directory is present and the go version in go.modis 1.14 or higher, the go command acts as if -mod=vendor were set.otherwise, the go command acts as if -mod=readonly were set.see https://golang.org/ref/mod#build-commands for details."
        )
        cacherw: None | bool = core.Field(
            default=None,
            cli=cli.Bool(name="-modcacherw"),
            description="Leave newly-created directories in the module cache read-writeinstead of making them read-only."
        )
        file: None | Path | str = core.Field(
            default=None,
            cli=cli.Str(name="-modfile"),
            description="In module aware mode, read (and possibly write) an alternate go.modfile instead of the one in the module root directory. a file named'go.mod' must still be present in order to determine the module rootdirectory, but it is not accessed. when -modfile is specified, analternate go.sum file is also used: its path is derived from the-modfile flag by trimming the '.mod' extension and appending '.sum'."
        )

    class Flags(cli.Options):
        gc: list[str] = core.Field(
            default_factory=list,
            cli=cli.List(name="-gcflags", surr="", equal="="),
            description="Arguments to pass on each go tool compile invocation."
        )
        ld: list[str] = core.Field(
            default_factory=list,
            cli=cli.List(name="-ldflags", surr="", equal="="),
            description="Arguments to pass on each go tool link invocation."
        )
        gccgo: list[str] = core.Field(
            default_factory=list,
            cli=cli.List(name="-gccgoflags", surr="", equal="="),
            description="Arguments to pass on each gccgo compiler/linker invocation."
        )
        asm: list[str] = core.Field(
            default_factory=list,
            cli=cli.List(name="-asmflags", surr="", equal="="),
            description="Arguments to pass on each go tool asm invocation."
        )

    output: None | Path | str = core.Field(
        default=None,
        cli=cli.File(name="-o"),
        description="Binary file output."
    )
    force: bool = core.Field(
        default=False,
        cli=cli.Bool(name="-a"),
        description="Force rebuilding of packages that are already up-to-date."
    )
    dry: None | bool = core.Field(
        default=None,
        cli=cli.Bool(name="-n"),
        description="Print the commands but do not run them."
    )
    job: None | int = core.Field(
        default=None,
        cli=cli.Int(name="-p"),
        description="The number of programs, such as build commands ortest binaries, that can be run in parallel.the default is gomaxprocs, normally the number of cpus available."
    )
    print: Print = core.Field(
        default_factory=Print,
        description="Print some info during building."
    )
    cover: Cover = core.Field(
        default_factory=Cover,
        description="Set the mode for coverage analysis.the default is 'set' unless -race is enabled,in which case it is 'atomic'.the values:set: bool: does this statement run?count: int: how many times does this statement run?atomic: int: count, but correct in multithreaded tests;significantly more expensive.sets -cover."
    )
    flags: Flags = core.Field(
        default_factory=Flags,
        description="Compiler, linker, gccgo and asm flags."
    )
    profiling: Profiling = core.Field(
        default_factory=Profiling,
        description="Profiling options."
    )
    work: None | bool = core.Field(
        default=None,
        cli=cli.Bool(name="-work"),
        description="Print the name of the temporary work directory anddo not delete it when exiting."
    )
    buildmode: None | str = core.Field(
        default=None,
        cli=cli.Str(name="-buildmode"),
        description="Build mode to use. see 'go help buildmode' for more."
    )
    buildvcs: None | bool = core.Field(
        default=None,
        cli=cli.Bool(name="-buildvcs"),
        description="Whether to stamp binaries with version control information('true', 'false', or 'auto'). by default ('auto'), version controlinformation is stamped into a binary if the main package, the main modulecontaining it, and the current directory are all in the same repository.use -buildvcs=false to always omit version control information, or-buildvcs=true to error out if version control information is available butcannot be included due to a missing tool or ambiguous directory structure."
    )
    compiler: None | str = core.Field(
        default=None,
        cli=cli.Str(name="-compiler"),
        description="Name of compiler to use, as in runtime.compiler (gccgo or gc)."
    )
    mod: Mod = core.Field(
        default_factory=Mod,
        description="Mod options."
    )
    installsuffix: None | str = core.Field(
        default=None,
        cli=cli.Str(name="-installsuffix"),
        description="A suffix to use in the name of the package installation directory,in order to keep output separate from default builds.if using the -race flag, the install suffix is automatically set to raceor, if set explicitly, has _race appended to it. likewise for the -msanand -asan flags. using a -buildmode option that requires non-default compileflags has a similar effect."
    )
    linkshared: None | bool = core.Field(
        default=None,
        cli=cli.Bool(name="-linkshared"),
        description="Build code that will be linked against shared libraries previouslycreated with -buildmode=shared."
    )
    overlay: None | Path | str = core.Field(
        default=None,
        cli=cli.Str(name="-overlay"),
        description="Read a json config file that provides an overlay for build operations.the file is a json struct with a single field, named 'replace', thatmaps each disk file path (a string) to its backing file path, so thata build will run as if the disk file path exists with the contentsgiven by the backing file paths, or as if the disk file path does notexist if its backing file path is empty. support for the -overlay flaghas some limitations: importantly, cgo files included from outside theinclude path must be in the same directory as the go package they areincluded from, and overlays will not appear when binaries and tests arerun through go run and go test respectively."
    )
    pgo: None | Path | str = core.Field(
        default=None,
        cli=cli.Str(name="-pgo"),
        description="Specify the file path of a profile for profile-guided optimization (pgo).when the special name 'auto' is specified, for each main package in thebuild, the go command selects a file named 'default.pgo' in the package'sdirectory if that file exists, and applies it to the (transitive)dependencies of the main package (other packages are not affected).special name 'off' turns off pgo. the default is 'auto'."
    )
    pkgdir: None | Path | str = core.Field(
        default=None,
        cli=cli.Str(name="-pkgdir"),
        description="Install and load all packages from dir instead of the usual locations.for example, when building with a non-standard configuration,use -pkgdir to keep generated packages in a separate location."
    )
    tags: list[str] = core.Field(
        default_factory=list,
        cli=cli.List(name="-tags"),
        description="A comma-separated list of additional build tags to consider satisfiedduring the build. for more information about build tags, see'go help buildconstraint'. (earlier versions of go used aspace-separated list, and that form is deprecated but still recognized.)"
    )
    trimpath: None | bool = core.Field(
        default=None,
        cli=cli.Bool(name="-trimpath"),
        description="Remove all file system paths from the resulting executable.instead of absolute file system paths, the recorded file nameswill begin either a module path@version (when using modules),or a plain import path (when using the standard library, or gopath)."
    )
    toolexec: list[str] = core.Field(
        default_factory=list,
        cli=cli.List(name="-toolexec"),
        description="A program to use to invoke toolchain programs like vet and asm.For example, instead of running asm, the go command will run'cmd args /path/to/asm <arguments for asm>'.The TOOLEXEC_IMPORTPATH environment variable will be set,matching 'go list -f {{.ImportPath}}' for the package being built."
    )
    source: list[str | Path] = core.Field(
        default_factory=list,
        cli=cli.Args(name="sources"),
        description="Source files / directories / packages."
    )


class Command(core.Model):
    shell: Shell = core.Field(
        default_factory=lambda: Shell(name="go", cmd=["go"]),
        description="Golang tool command."
    )


class Mod(Command):
    @core.typeguard
    def tidy(self, compat: str = "") -> Shell:
        shell = self.shell
        shell.cmd += ["mod", "tidy"]
        if compat.strip():
            shell.cmd.append(f"compat={compat.strip()}")
        return shell

    @core.typeguard
    def vendor(self, outdir: None | Path = None):
        shell = self.shell
        shell.cmd += ["mod", "vendor"]
        if outdir:
            out = Path(outdir).expanduser().resolve().absolute()
            shell.cmd.append(f"-o={out}")
        return shell


class Go:
    @property
    def shell(self) -> Shell:
        return self._shell

    @shell.setter
    def shell(self, value: Shell):
        self._shell = value

    def __init__(self):
        self._shell = Shell(name="go", cmd=["go"])
        self._mod = Mod()

    @property
    def mod(self) -> Mod:
        result = copy.deepcopy(self._mod)
        result.shell = copy.deepcopy(self._shell)
        return result

    def build(self, options: BuildOptions):
        opt = options.serialize()
        shell = copy.deepcopy(self._shell)
        shell.cmd.append("build")
        shell.cmd += opt
        shell.sync()
