from typing import Optional

from umk import core, kit
from umk.framework.filesystem import Path


# ####################################################################################
# Client
# ####################################################################################


class ClientConfig(kit.cli.Options):
    config: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--config"),
        description="Location of client config files (default '/home/${USER}/.docker')"
    )
    context: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--context"),
        description="Name of the context to use to connect to the daemon (overrides DOCKER_HOST env var and default context set with 'docker context use')"
    )
    debug: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--debug"),
        description="Enable debug mode"
    )
    host: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--host"),
        description="Daemon socket to connect to"
    )
    log_level: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--log-level"),
        description="Set the logging level ('debug', 'info', 'warn', 'error', 'fatal') (default 'info')"
    )
    tls: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--tls"),
        description="Use TLS; implied by"
    )
    tlscacert: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--tlscacert"),
        description="Trust certs signed only by this CA (default '/home/edward/.docker/ca.pem')"
    )
    tlscert: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--tlscert"),
        description="Path to TLS certificate file (default '/home/edward/.docker/cert.pem')"
    )
    tlskey: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--tlskey"),
        description="Path to TLS key file (default '/home/edward/.docker/key.pem')"
    )
    tlsverify: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--tlsverify"),
        description="Use TLS and verify the remote"
    )
    version: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--version"),
        description="Print version information and quit"
    )


# ####################################################################################
# Image
# ####################################################################################


class ImageBuild(kit.cli.Options):
    add_host: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--add-host", equal="=", equal_each=":", surr='"'),
        description="Add a custom host-to-IP mapping (format: 'host:ip')"
    )
    allow: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--allow", equal="=", surr='"'),
        description="Allow extra privileged entitlement (e.g., 'network.host', 'security.insecure')")
    attest: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--attest"),
        description="Attestation parameters (format: 'type=sbom,generator=image')"
    )
    build_arg: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--build-arg"),
        description="Set build-time variables"
    )
    build_context: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--build-context"),
        description="Additional build contexts (e.g., name=path)"
    )
    builder: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--builder"),
        description="Override the configured builder instance (default 'default')"
    )
    cache_from: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--cache-from"),
        description="External cache sources (e.g., 'user/app:cache', 'type=local,src=path/to/dir')"
    )
    cache_to: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--cache-to"),
        description="Cache export destinations (e.g., 'user/app:cache', 'type=local,dest=path/to/dir')"
    )
    cgroup_parent: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cgroup-parent"),
        description="Optional parent cgroup for the container"
    )
    file: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--file"),
        description="Name of the Dockerfile (default: 'path/Dockerfile')"
    )
    iidfile: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--iidfile"),
        description="Write the image ID to the file"
    )
    label: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--label"),
        description="Set metadata for an image"
    )
    load: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--load"),
        description="Shorthand for '--output=type=docker'"
    )
    metadata_file: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--metadata-file"),
        description="Write build result metadata to the file"
    )
    network: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--network"),
        description="Set the networking mode for the 'RUN' instructions during build (default 'default')"
    )
    no_cache: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--no-cache"),
        description="Do not use cache when building the image"
    )
    no_cache_filter: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--no-cache-filter"),
        description="Do not cache specified stages"
    )
    output: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--output", equal_each="=", split=","),
        description="Output destination (format: 'type=local,dest=path')"
    )
    platform: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--platform"),
        description="Set target platform for build"
    )
    progress: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--progress"),
        description="Set type of progress output ('auto', 'plain', 'tty'). Use plain to show container output (default 'auto')"
    )
    provenance: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--provenance"),
        description="Shorthand for '--attest=type=provenance'"
    )
    pull: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--pull"),
        description="Always attempt to pull all referenced images"
    )
    push: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--push"),
        description="Shorthand for '--output=type=registry'"
    )
    quiet: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--quiet"),
        description="Suppress the build output and print image ID on success"
    )
    sbom: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--sbom"),
        description="Shorthand for '--attest=type=sbom'"
    )
    secret: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--secret"),
        description="Secret to expose to the build (format: 'id=mysecret[,src=/local/secret]')"
    )
    shm_size: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--shm-size"),
        description="Size of '/dev/shm'"
    )
    ssh: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--ssh"),
        description="SSH agent socket or keys to expose to the build (format: 'default|<id>[=<socket>|<key>[,<key>]]')"
    )
    tag: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--tag", multi=True),
        description="Name and optionally a tag (format: 'name[:tag]')"
    )
    target: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--target"),
        description="Set the target build stage to build"
    )
    path: Path = core.Field(
        cli=kit.cli.Arg(name="path")
    )


class ImageImport(kit.cli.Options):
    change: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--change"),
        description="Apply Dockerfile instruction to the created image"
    )
    message: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--message"),
        description="Set commit message for imported image"
    )
    platform: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--platform"),
        description="Set platform if server is multi-platform capable"
    )
    file: Path = core.Field(
        cli=kit.cli.Arg(name="file")
    )
    repository: str = core.Field(
        cli=kit.cli.Arg(name="repository")
    )


class ImagePull(kit.cli.Options):
    all_tags: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--all-tags"),
        description="Download all tagged images in the repository"
    )
    disable_content_trust: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--disable-content-trust"),
        description="Skip image verification (default true)"
    )
    platform: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--platform"),
        description="Set platform if server is multi-platform capable"
    )
    repository: str = core.Field(
        cli=kit.cli.Arg(name="repository")
    )


class ImagePush(kit.cli.Options):
    all_tags: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--all-tags"),
        description="Download all tagged images in the repository"
    )
    disable_content_trust: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--disable-content-trust"),
        description="Skip image verification (default true)"
    )
    platform: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--platform"),
        description="Set platform if server is multi-platform capable"
    )
    name: str = core.Field(
        cli=kit.cli.Arg(name="repository")
    )


# ####################################################################################
# Containers
# ####################################################################################


class ContainerCommit(kit.cli.Options):
    author: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--author", surr='"'),
        description="Author (e.g., 'John Hannibal Smith <hannibal@a-team.com>')"
    )
    change: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--change", surr='"'),
        description="Apply Dockerfile instruction to the created image"
    )

    message: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--message", surr='"'),
        description="Commit message"
    )
    container: str = core.Field(
        cli=kit.cli.Arg(name="container")
    )
    repository: str = core.Field(
        cli=kit.cli.Arg(name="repository")
    )


class ContainerCreate(kit.cli.Options):
    add_host: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--add-host"),
        description="Add a custom host-to-IP mapping (host:ip)"
    )
    attach: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--attach"),
        description="Attach to STDIN, STDOUT or STDERR"
    )
    blkio_weight: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--blkio-weight"),
        description="Block IO (relative weight), between 10 and 1000, or 0 to disable (default 0)"
    )
    blkio_weight_device: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--blkio-weight-device"),
        description="Block IO weight (relative device weight) (default [])"
    )
    cap_add: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--cap-add"),
        description="Add Linux capabilities"
    )
    cap_drop: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--cap-drop"),
        description="Drop Linux capabilities"
    )
    cgroup_parent: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cgroup-parent"),
        description="Optional parent cgroup for the container"
    )
    cgroupns: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cgroupns"),
        description="Cgroup namespace to use (host|private)"
                    "   'host': Run the container in the Docker host's cgroup namespace"
                    "'private': Run the container in its own private cgroup namespace"
    )
    cidfile: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cidfile"),
        description="Write the container ID to the file"
    )
    cpu_period: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-period"),
        description="Limit CPU CFS (Completely Fair Scheduler) period"
    )
    cpu_quota: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-quota"),
        description="Limit CPU CFS (Completely Fair Scheduler) quota"
    )
    cpu_rt_period: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-rt-period"),
        description="Limit CPU real-time period in microseconds"
    )
    cpu_rt_runtime: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-rt-runtime"),
        description="Limit CPU real-time runtime in microseconds"
    )
    cpu_shares: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-shares"),
        description="CPU shares (relative weight)"
    )
    cpus: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpus"),
        description="Number of CPUs"
    )
    cpuset_cpus: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cpuset-cpus"),
        description="CPUs in which to allow execution (0-3, 0,1)"
    )
    cpuset_mems: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cpuset-mems"),
        description="MEMs in which to allow execution (0-3, 0,1)"
    )
    device: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device"),
        description="Add a host device to the container"
    )
    device_cgroup_rule: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device-cgroup-rule"),
        description="Add a rule to the cgroup allowed devices list"
    )
    device_read_bps: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device-read-bps"),
        description="Limit read rate (bytes per second) from a device (default [])"
    )
    device_read_iops: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device-read-iops"),
        description="Limit read rate (IO per second) from a device (default [])"
    )
    device_write_bps: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device-write-bps"),
        description="Limit write rate (bytes per second) to a device (default [])"
    )
    device_write_iops: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--device-write-iops"),
        description="Limit write rate (IO per second) to a device (default [])"
    )
    disable_content_trust: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--disable-content-trust"),
        description="Skip image verification (default true)"
    )
    dns: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--dns"),
        description="Set custom DNS servers"
    )
    dns_option: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--dns-option"),
        description="Set DNS options"
    )
    dns_search: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--dns-search"),
        description="Set custom DNS search domains"
    )
    domainname: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--domainname"),
        description="Container NIS domain name"
    )
    entrypoint: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--entrypoint"),
        description="Overwrite the default ENTRYPOINT of the image"
    )
    env: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--env"),
        description="Set environment variables"
    )
    env_file: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--env-file"),
        description="Read in a file of environment variables"
    )
    expose: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--expose"),
        description="Expose a port or a range of ports"
    )
    gpus: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--gpus"),
        description="GPU devices to add to the container ('all' to pass all GPUs)"
    )
    group_add: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--group-add"),
        description="Add additional groups to join"
    )
    health_cmd: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--health-cmd"),
        description="Command to run to check health"
    )
    health_interval: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--health-interval"),
        description="Time between running the check (ms|s|m|h) (default 0s)"
    )
    health_retries: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--health-retries"),
        description="Consecutive failures needed to report unhealthy"
    )
    health_start_period: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--health-start-period"),
        description="Start period for the container to initialize before starting health-retries countdown (ms|s|m|h) (default 0s)"
    )
    health_timeout: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--health-timeout"),
        description="Maximum time to allow one check to run (ms|s|m|h) (default 0s)"
    )
    help: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--help"),
        description="Print usage"
    )
    hostname: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--hostname"),
        description="Container host name"
    )
    init: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--init"),
        description="Run an init inside the container that forwards signals and reaps processes"
    )
    interactive: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--interactive"),
        description="Keep STDIN open even if not attached"
    )
    ip: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--ip"),
        description="IPv4 address (e.g., 172.30.100.104)"
    )
    ip6: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--ip6"),
        description="IPv6 address (e.g., 2001:db8::33)"
    )
    ipc: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--ipc"),
        description="IPC mode to use"
    )
    isolation: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--isolation"),
        description="Container isolation technology"
    )
    kernel_memory: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--kernel-memory"),
        description="Kernel memory limit"
    )
    label: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--label"),
        description="Set meta data on a container"
    )
    label_file: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--label-file"),
        description="Read in a line delimited file of labels"
    )
    link: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--link"),
        description="Add link to another container"
    )
    link_local_ip: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--link-local-ip"),
        description="Container IPv4/IPv6 link-local addresses"
    )
    log_driver: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--log-driver"),
        description="Logging driver for the container"
    )
    log_opt: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--log-opt"),
        description="Log driver options"
    )
    mac_address: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--mac-address"),
        description="Container MAC address (e.g., 92:d0:c6:0a:29:33)"
    )
    memory: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory"),
        description="Memory limit"
    )
    memory_reservation: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory-reservation"),
        description="Memory soft limit"
    )
    memory_swap: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory-swap"),
        description="Swap limit equal to memory plus swap: '-1' to enable unlimited swap"
    )
    memory_swappiness: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory-swappiness"),
        description="Tune container memory swappiness (0 to 100) (default"
    )
    mount: list = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--mount"),
        description="Attach a filesystem mount to the container"
    )
    name: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--name"),
        description="Assign a name to the container"
    )
    network: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--network"),
        description="Connect a container to a network"
    )
    network_alias: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--network-alias"),
        description="Add network-scoped alias for the container"
    )
    no_healthcheck: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--no-healthcheck"),
        description="Disable any container-specified HEALTHCHECK"
    )
    oom_kill_disable: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--oom-kill-disable"),
        description="Disable OOM Killer"
    )
    oom_score_adj: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--oom-score-adj"),
        description="Tune host's OOM preferences (-1000 to 1000)"
    )
    pid: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--pid"),
        description="PID namespace to use"
    )
    pids_limit: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--pids-limit"),
        description="Tune container pids limit (set for unlimited)"
    )
    platform: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--platform"),
        description="Set platform if server is multi-platform capable"
    )
    privileged: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--privileged"),
        description="Give extended privileges to this container"
    )
    publish: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--publish"),
        description="Publish a container's port(s) to the host"
    )
    publish_all: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--publish-all"),
        description="Publish all exposed ports to random ports"
    )
    pull: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--pull"),
        description="Pull image before creating ('always', '|missing', 'never') (default 'missing')"
    )
    quiet: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--quiet"),
        description="Suppress the pull output"
    )
    read_only: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--read-only"),
        description="Mount the container's root filesystem as read only"
    )
    restart: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--restart"),
        description="Restart policy to apply when a container exits (default 'no')"
    )
    rm: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--rm"),
        description="Automatically remove the container when it exits"
    )
    runtime: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--runtime"),
        description="Runtime to use for this container"
    )
    security_opt: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--security-opt"),
        description="Security Options"
    )
    shm_size: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--shm-size"),
        description="Size of /dev/shm"
    )
    stop_signal: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--stop-signal"),
        description="Signal to stop the container"
    )
    stop_timeout: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--stop-timeout"),
        description="Timeout (in seconds) to stop a container"
    )
    storage_opt: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--storage-opt"),
        description="Storage driver options for the container"
    )
    sysctl: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--sysctl", equal_each="=", split=","),
        description="Sysctl options (default map[])"
    )
    tmpfs: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--tmpfs"),
        description="Mount a tmpfs directory"
    )
    tty: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--tty"),
        description="Allocate a pseudo-TTY"
    )
    ulimit: list = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--ulimit"),
        description="Ulimit options (default [])"
    )
    user: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--user"),
        description="Username or UID (format: <name|uid>[:<group|gid>])"
    )
    userns: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--userns"),
        description="User namespace to use"
    )
    uts: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--uts"),
        description="UTS namespace to use"
    )
    volume: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--volume"),
        description="Bind mount a volume"
    )
    volume_driver: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--volume-driver"),
        description="Optional volume driver for the container"
    )
    volumes_from: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--volumes-from"),
        description="Mount volumes from the specified container(s)"
    )
    workdir: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--workdir"),
        description="Working directory inside the container"
    )
    image: str = core.Field(
        cli=kit.cli.Arg(name="image"),
        description="Container image (id or name)",
    )
    cmd: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.Args(name="command")
    )


class ContainerExec(kit.cli.Options):
    detach: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--detach"),
        description="Detached mode: run command in the background"
    )
    detach_keys: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--detach-keys"),
        description="Override the key sequence for detaching a container"
    )
    env: dict[str, str] = core.Field(
        default_factory=dict,
        cli=kit.cli.Dict(name="--env", equal_each="=", multi=True),
        description="Set environment variables"
    )
    env_file: list[str] = core.Field(
        default_factory=list,
        cli=kit.cli.List(name="--env-file"),
        description="Read in a file of environment variables"
    )
    interactive: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--interactive"),
        description="Keep STDIN open even if not attached"
    )
    privileged: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--privileged"),
        description="Give extended privileges to the command"
    )
    tty: None | bool = core.Field(
        default=None,
        cli=kit.cli.Bool(name="--tty"),
        description="Allocate a pseudo-TTY"
    )
    user: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--user"),
        description="Username or UID (format: '<name|uid>[:<group|gid>]')"
    )
    workdir: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--workdir"),
        description="Working directory inside the container"
    )
    container: str = core.Field(
        cli=kit.cli.Arg(name="command")
    )
    cmd: list[str] = core.Field(
        cli=kit.cli.Args(name="command")
    )


class ContainerUpdate(kit.cli.Options):
    blkio_weight: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--blkio-weight"),
        description="Block IO (relative weight), between 10 and 1000, or 0 to disable (default 0)"
    )
    cpu_period: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-period"),
        description="Limit CPU CFS (Completely Fair Scheduler) period"
    )
    cpu_quota: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-quota"),
        description="Limit CPU CFS (Completely Fair Scheduler) quota"
    )
    cpu_rt_period: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-rt-period"),
        description="Limit the CPU real-time period in microseconds"
    )
    cpu_rt_runtime: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-rt-runtime"),
        description="Limit the CPU real-time runtime in microseconds"
    )
    cpu_shares: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpu-shares"),
        description="CPU shares (relative weight)"
    )
    cpus: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--cpus"),
        description="Number of CPUs"
    )
    cpuset_cpus: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cpuset-cpus"),
        description="CPUs in which to allow execution (0-3, 0,1)"
    )
    cpuset_mems: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--cpuset-mems"),
        description="MEMs in which to allow execution (0-3, 0,1)"
    )
    memory: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory"),
        description="Memory limit"
    )
    memory_reservation: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory-reservation"),
        description="Memory soft limit"
    )
    memory_swap: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--memory-swap"),
        description="Swap limit equal to memory plus swap: to enable unlimited swap"
    )
    pids_limit: None | int = core.Field(
        default=None,
        cli=kit.cli.Int(name="--pids-limit"),
        description="Tune container pids limit (set for unlimited)"
    )
    restart: None | str = core.Field(
        default=None,
        cli=kit.cli.Str(name="--restart"),
        description="Restart policy to apply when a container exits"
    )
