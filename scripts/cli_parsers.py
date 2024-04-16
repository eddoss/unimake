from pydantic import BaseModel
from pydantic import Field as BaseField


class Option(BaseModel):
    @property
    def name(self) -> str:
        return max(self.flags, key=len)

    flags: list[str] = BaseField(
        default_factory=list,
        description="CLI option/argument/flag/... names (i.e. -f, --format, -tags ...)."
    )
    description: str = BaseField(
        default="",
        description="CLI option/argument/flag/... description."
    )
    type: str = BaseField(
        default="",
        description="CLI option parsed type (any string, some times it may stringArray, strings, lists, bytes, int ...)"
    )


class Field(BaseModel):
    name: str = BaseField(
        default="",
        description="Field name."
    )
    description: str = BaseField(
        default="",
        description="Field description."
    )
    type: str = BaseField(
        default="",
        description="Field type"
    )
    default: str = BaseField(
        default="",
        description="Field default value"
    )
    creatable: bool = BaseField(
        default=False,
        description="Whether default value is constant or creates by factory."
    )
    cli: str = BaseField(
        default="",
        description="'cli' attribute value (as string)."
    )


class Builder(BaseModel):
    class Defaults(BaseModel):
        values: dict[str, str] = BaseField(
            description="Map of the types and its default values.",
            default_factory=lambda: {
                "str": '""',
                "int": "0",
                "float": "0.0",
                "bool": "False",
                "None | str": "None",
                "None | int": "None",
                "None | float": "None",
                "None | bool": "None",
            }
        )
        factories: dict[str, str] = BaseField(
            description="Map of the types and its default factories.",
            default_factory=lambda: {
                "list": "list",
                "list[str]": "list",
                "list[int]": "list",
                "list[float]": "list",
                "list[bool]": "list",
                "dict": "dict",
                "dict[str, str]": "dict",
                "dict[str, int]": "dict",
                "dict[str, float]": "dict",
                "dict[str, bool]": "dict",
                "dict[int, str]": "dict",
                "dict[int, int]": "dict",
                "dict[int, bool]": "dict",
                "dict[int, float]": "dict",
                "dict[float, str]": "dict",
                "dict[float, int]": "dict",
                "dict[float, float]": "dict",
            }
        )
    types: dict[str | None, str] = BaseField(
        description="Map of the raw type (strings, lists, bytes, int, ...) and real type (int, bool, ...)."
    )
    defaults: Defaults = BaseField(
        default_factory=Defaults,
        description="Map of the types and its default values/factories."
    )
    cli: dict[str | None, str] = BaseField(
        description="Map of the types and its cli.TYPE.",
        default_factory=lambda: {
            "list": 'cli.List(name="$option.name")',
            "list[str]": 'cli.List(name="$option.name")',
            "list[int]": 'cli.List(name="$option.name")',
            "list[float]": 'cli.List(name="$option.name")',
            "list[bool]": 'cli.List(name="$option.name")',
            "dict": 'cli.Dict(name="$option.name")',
            "dict[str, str]": 'cli.Dict(name="$option.name")',
            "dict[str, int]": 'cli.Dict(name="$option.name")',
            "dict[str, float]": 'cli.Dict(name="$option.name")',
            "dict[str, bool]": 'cli.Dict(name="$option.name")',
            "dict[int, str]": 'cli.Dict(name="$option.name")',
            "dict[int, int]": 'cli.Dict(name="$option.name")',
            "dict[int, bool]": 'cli.Dict(name="$option.name")',
            "dict[int, float]": 'cli.Dict(name="$option.name")',
            "dict[float, str]": 'cli.Dict(name="$option.name")',
            "dict[float, int]": 'cli.Dict(name="$option.name")',
            "dict[float, float]": 'cli.Dict(name="$option.name")',
            "int": 'cli.Int(name="$option.name")',
            "str": 'cli.Str(name="$option.name")',
            "bool": 'cli.Bool(name="$option.name")',
            "None | int": 'cli.Int(name="$option.name")',
            "None | str": 'cli.Str(name="$option.name")',
            "None | bool": 'cli.Bool(name="$option.name")',
            "None | Path": 'cli.File(name="$option.name")',
            "None | Path | str": 'cli.File(name="$option.name")',
            "": 'cli.Obj(name="$option.name")',
            "None": 'cli.Obj(name="$option.name")',
        }
    )

    def substitute(self, string: str, option: Option, field: Field):
        result = string.replace("$option.name", option.name).replace("$option.description", option.description)
        result = result.replace("$option.type", option.type)
        result = result.replace("$field.name", field.name)
        result = result.replace("$field.description", field.description)
        result = result.replace("$field.type", field.type)
        return result

    def build(self, options: list[Option]) -> list[Field]:
        result = []
        for option in options:
            option.description = option.description.strip()
            field = Field()
            field.name = option.name.strip("--").replace("-", "_").replace(".", "_")
            field.type = self.types.get(option.type, "<empty_type>")
            field.description = option.description.replace("\n", " ").replace('"', "'")
            field.default = self.defaults.values.get(field.type)
            if not field.default:
                field.default = self.defaults.factories.get(field.type)
                field.creatable = field.default is not None
            field.cli = self.cli.get(field.type)
            if field.cli:
                field.cli = self.substitute(field.cli, option, field)
            result.append(field)
        return result


def show(fields: list[Field], class_name: str, class_parent="cli.Options"):
    if class_parent:
        print(f"class {class_name}({class_parent}):")
    else:
        print(f"class {class_name}:")
    for field in fields:
        factory = ["default", "default_factory"][int(field.creatable)]
        print(f'    {field.name}: {field.type} = core.Field(\n        {factory}={field.default},\n        cli={field.cli},\n        description="{field.description}"\n    )')


def docker(struct: str, raw: str):
    builder = Builder(
        types={
            "strings": "list[str]",
            "list": "list[str]",
            "ulimit": "list",
            "mound": "list",
            "stringArray": "dict[str, str]",
            "filter": "dict[str, str]",
            "string": "None | str",
            "uint16": "None | int",
            "int": "None | int",
            "decimal": "None | int",
            "duration": "None | int",
            "": "None | bool",
            None: "None | bool"
        }
    )

    raw = raw.strip()
    if not raw:
        return

    options = []
    for line in raw.split("\n"):
        line = line.strip()
        option = Option()
        chunks = line.split()
        for chunk in chunks:
            if chunk.startswith("--"):
                option.flags.append(chunk)
            elif chunk.startswith("-"):
                if chunk.endswith(","):
                    chunk = chunk.rstrip(",")
                option.flags.append(chunk)
            elif not option.type:
                if not option.description and not chunk.istitle():
                    option.type = chunk
                else:
                    option.description += chunk + " "
            else:
                option.description += chunk + " "
        options.append(option)

    fields = builder.build(options)
    show(fields, struct)


def golang(struct: str, raw: str):
    builder = Builder(
        types={
            "n": "None | int",
            "id": "None | int",
            "rate": "None | int",
            "int": "None | int",
            "mode": "None | str",
            "bool": "None | bool",
            "prefix": "None | str",
            "note": "None | str",
            "entry": "None | str",
            "type": "None | str",
            "linker": "None | str",
            "quantum": "None | str",
            "symbol": "None | str",
            "name": "None | str",
            "string": "None | str",
            "suffix": "None | str",
            "list": "list[str]",
            "value": "list[str]",
            "directory": "None | Path | str",
            "dir": "None | Path | str",
            "file": "None | Path | str",
            "path": "None | Path | str",
        }
    )

    raw = raw.strip()
    if not raw:
        return

    valid_types = set(builder.types.keys())

    options = []
    option: Option | None = None
    for line in raw.split("\n"):
        if not line.startswith(" "):
            if option:
                option.description = option.description.capitalize()
                options.append(option)
            option = Option()
            split = line.strip().split()
            option.flags.append(split[0])
            if len(split) > 1:
                option.type = split[1]
            else:
                option.type = "bool"
            if option.type not in valid_types:
                option.type = ""
        else:
            option.description += line.strip() + ""
    options.append(option)

    fields = builder.build(options)
    show(fields, struct)


golang(
    struct="BuildOptions",
    raw="""
-B note
    add an ELF NT_GNU_BUILD_ID note when using ELF
-E entry
    set entry symbol name
-H type
    set header type
-I linker
    use linker as ELF dynamic linker
-L directory
    add specified directory to library path
-R quantum
    set address rounding quantum (default -1)
-T int
    set the start address of text symbols (default -1)
-V	
    print version and exit
-X definition
    add string value definition of the form importpath.name=value
-asan
    enable ASan interface
-aslr
    enable ASLR for buildmode=c-shared on windows (default true)
-benchmark string
    set to 'mem' or 'cpu' to enable phase benchmarking
-benchmarkprofile base
    emit phase profiles to base_phase.{cpu,mem}prof
-buildid id
    record id as Go toolchain build id
-buildmode mode
    set build mode
-c	
    dump call graph
-capturehostobjs string
    capture host object files loaded during internal linking to specified dir
-compressdwarf
    compress DWARF if possible (default true)
-cpuprofile file
    write cpu profile to file
-d	
    disable dynamic executable
-debugnosplit
    dump nosplit call graph
-debugtextsize int
    debug text section max size
-debugtramp int
    debug trampolines
-dumpdep
    dump symbol dependency graph
-extar string
    archive program for buildmode=c-archive
-extld linker
    use linker when linking in external mode
-extldflags flags
    pass flags to external linker
-f	
    ignore version mismatch
-g	
    disable go package data checks
-h	
    halt on error
-importcfg file
    read import configuration from file
-installsuffix suffix
    set package directory suffix
-k symbol
    set field tracking symbol
-libgcc string
    compiler support lib for internal linking; use "none" to disable
-linkmode mode
    set link mode
-linkshared
    link against installed Go shared libraries
-memprofile file
    write memory profile to file
-memprofilerate rate
    set runtime.MemProfileRate to rate
-msan
    enable MSan interface
-n	
    dump symbol table
-o file
    write output to file
-pluginpath string
    full path name for plugin
-pruneweakmap
    prune weak mapinit refs (default true)
-r path
    set the ELF dynamic linker search path to dir1:dir2:...
-race
    enable race detector
-s	
    disable symbol table
-strictdups int
    sanity check duplicate symbol contents during object file reading (1=warn 2=err).
-tmpdir directory
    use directory for temporary files
-v	
    print link trace
-w	
    disable DWARF generation
""")

# def show_cmd(text: str):
#     text = text.strip()
#     if not text:
#         return
#     for line in text.split("\n"):
#         line = line.strip()
#         chunks = line.split()
#         cmd = chunks[0]
#         des = "".join(chunks[1:])
#         print(
#             f"\ndef {cmd}(self):\n"
#             f"    pass"
#         )
