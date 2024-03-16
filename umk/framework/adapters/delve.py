from umk.framework.filesystem import Path
from umk.framework.system import Shell, Environs
from umk import globals, core, kit


class Options(kit.cli.Options):
    accept_multiclient: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--accept-multiclient"),
        description="Allows a headless server to accept multiple client connections via JSON-RPC or DAP."
    )
    allow_non_terminal_interactive: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--allow-non-terminal-interactive"),
        description="Allows interactive sessions of Delve that don't have a terminal as stdin, stdout and stderr"
    )
    api_version: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--api-version"),
        description="Selects JSON-RPC API version when headless. New clients should use v2. Can be reset via RPCServer.SetApiVersion."
    )
    backend: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--backend"),
        description="Backend selection (see 'dlv help backend')."
    )
    build_flags: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--build-flags"),
        description="Build flags, to be passed to the compiler."
    )
    check_go_version: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--check-go-version"),
        description="Exits if the version of Go in use is not compatible (too old or too new) with the version of Delve."
    )
    disable_aslr: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--disable-aslr"),
        description="Disables address space randomization"
    )
    headless: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--headless"),
        description="Run debug server only, in headless mode. Server will accept both JSON-RPC or DAP client connections."
    )
    init: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--init"),
        description="Init file, executed by the terminal client."
    )
    listen: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--listen"),
        description="Debugging server listen address (default 127.0.0.1:0)."
    )
    log: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--log"),
        description="Enable debugging server logging."
    )
    log_dest: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--log-dest"),
        description="Writes logs to the specified file or file descriptor."
    )
    log_output: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--log-output"),
        description="Comma separated list of components that should produce debug output."
    )
    only_same_user: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--only-same-user"),
        description="Only connections from the same user that started this instance of Delve are allowed to connect."
    )
    redirect: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--redirect"),
        description="Specifies redirect rules for target process."
    )
    wd: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--wd"),
        description="Working directory for running the program."
    )


class Delve(core.Model):
    cmd: list[str | Path] = core.Field(
        default_factory=lambda: ["dlv"],
        description="Delve command."
    )
    options: Options = core.Field(
        default_factory=Options,
        description="Delve main options."
    )
    workdir: Path = core.Field(
        default_factory=lambda: globals.paths.work,
        description="Working directory."
    )
    environs: None | Environs = core.Field(
        default=None,
        description="Shell environment variables."
    )

    @property
    def shell(self) -> Shell:
        result = Shell(name="delve")
        result.cmd = self.cmd
        result.cmd += self.options.serialize()
        result.environs = self.environs
        return result

    @core.typeguard
    def attach(self, pid: int, executable: str = '', continues: bool = False) -> Shell:
        shell = self.shell
        shell.cmd += ["attach", str(pid)]
        if executable:
            shell.cmd.append(executable)
        if continues:
            shell.cmd.append("--continue")
        return shell

    @core.typeguard
    def exec(self, cmd: list[str], continues: bool = False, tty: str = "") -> Shell:
        shell = self.shell
        shell.cmd += ["exec"]
        if tty:
            shell.cmd += [f"--tty={tty}"]
        if continues:
            shell.cmd.append("--continue")
        shell.cmd.append(cmd[0])
        if len(cmd) > 1:
            shell.cmd.append("--")
            self.cmd += cmd[1:]
        return shell
