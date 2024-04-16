import copy
import os

import yaml

from umk import core
from umk.framework.utils import cli
from umk.core.typings import Any
from umk.framework.filesystem import Path


# ####################################################################################
# Service models
# ####################################################################################

class Build(cli.NoEmpty):
    context: None | Path | str = core.Field(
        default=None,
        description="Either a path to a directory containing a Dockerfile, or a url to a git repository."
    )
    dockerfile: None | str = core.Field(
        default=None,
        description="Alternate Dockerfile name (relative to build context)."
    )
    args: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Build arguments."
    )
    ssh: str | dict[str, Any] = core.Field(
        default=None,
        description="SSH authentications that the image builder should use during image build (e.g., cloning private repository)"
    )
    cache_from: list[str] = core.Field(
        default_factory=list,
        description="List of sources the image builder should use for cache resolution."
    )
    cache_to: list[str] = core.Field(
        default_factory=list,
        description="List of export locations to be used to share build cache with future builds."
    )
    additional_context: dict[str, str | Path] = core.Field(
        default_factory=dict,
        description="List of named contexts the image builder should use during image build"
    )
    extra_hosts: dict[str, str] = core.Field(
        default_factory=dict,
        description="Adds hostname mappings at build-time. Use the same syntax as extra_hosts."
    )
    isolation: None | str = core.Field(
        default=None,
        description="Specifies a build’s container isolation technology. Like isolation, supported values are platform specific."
    )
    privileged: None | bool = core.Field(
        default=None,
        description="Configures the service image to build with elevated privileges. Support and actual impacts are platform specific."
    )
    labels: dict[str, str] = core.Field(
        default_factory=dict,
        description="Metadata to the resulting image. labels can be set either as an array or a map."
    )
    no_cache: None | bool = core.Field(
        default=None,
        description="Disables image builder cache and enforces a full rebuild from source for all image layers. This only applies to layers declared in the Dockerfile, referenced images COULD be retrieved from local image store whenever tag has been updated on registry"
    )
    pull: None | bool = core.Field(
        default=None,
        description="Requires the image builder to pull referenced images (FROM Dockerfile directive), even if those are already available in the local image store"
    )
    network: None | str = core.Field(
        default=None,
        description="Set the network containers connect to for the RUN instructions during build."
    )
    shm_size: None | int | str = core.Field(
        default=None,
        description="Sets the size of the shared memory (/dev/shm partition on Linux) allocated for building Docker images. Specify as an integer value representing the number of bytes or as a string expressing a byte value."
    )
    target: None | str = core.Field(
        default=None,
        description="The stage to build as defined inside a multi-stage Dockerfile."
    )
    secrets: list[str] = core.Field(
        default_factory=list,
        description="Grants access to sensitive data defined by secrets on a per-service build basis."
    )
    tags: dict[str, str] = core.Field(
        default_factory=dict,
        description="Dict of tag mappings that must be associated to the build image."
    )
    platforms: list[str] = core.Field(
        default_factory=list,
        description="List of target platforms."
    )

    @core.field.serializer('args')
    def serialize_args(self, value: dict[str, str], _info):
        res = copy.deepcopy(value)
        for name in res:
            val = res[name]
            if " " in val:
                res[name] = f'"{val}"'
        return res

    @core.field.serializer('ssh')
    def serialize_ssh(self, value: str | dict[str, str], _info):
        if not value:
            return []
        if issubclass(type(value), str):
            return [value]
        res = []
        for k, v in value.items():
            if " " in v:
                res.append(f'{k}="{v}"')
            else:
                res.append(f'{k}={v}')
        return res

    @core.field.serializer('extra_hosts')
    def serialize_extra_hosts(self, value: dict[str, str], _info):
        return {k: f'"{v}"' for k, v in value.items()}

    @core.field.serializer('labels')
    def serialize_labels(self, value: dict[str, str], _info):
        res = copy.deepcopy(value)
        for name in res:
            res[name] = f'"{res[name]}"'
        return res

    @core.field.serializer('tags')
    def serialize_tags(self, value: dict[str, str], _info):
        res = []
        for k, v in value.items():
            k = k.strip()
            v = v.strip()
            if not k:
                continue
            if v:
                res.append(f"{k}:{v}")
            else:
                res.append(f"{k}")
        return res


class BlockIo(cli.NoEmpty):
    class Weight(cli.NoEmpty):
        path: str | Path
        weight: int

    class Rate(cli.NoEmpty):
        path: str | Path
        rate: int | str

    weight: int = None
    weight_device: list[Weight] = core.Field(default_factory=list)
    device_read_bps: list[Rate] = core.Field(default_factory=list)
    device_read_iops: list[Rate] = core.Field(default_factory=list)
    device_write_bps: list[Rate] = core.Field(default_factory=list)
    device_write_iops: list[Rate] = core.Field(default_factory=list)


class Credential(cli.NoEmpty):
    file: str | Path = core.Field(None)
    registry: str = core.Field(None)
    config: str = core.Field(None)


class Dependency(cli.NoEmpty):
    name: str = core.Field(None)
    condition: str = core.Field(None)
    restart: bool = core.Field(None)


class Placement(cli.NoEmpty):
    constraints: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Defines a required property the platform's node must fulfill to run the service container. It can be set either by a list or a map with string values."
    )
    preferences: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Defines a property the platform's node should fulfill to run service container. It can be set either by a list or a map with string values."
    )


class Device(cli.NoEmpty):
    capabilities: list[str] = core.Field(
        default_factory=list,
        description="List of the generic and driver specific capabilities."
    )
    driver: None | str = core.Field(
        default=None,
        description="A different driver for the reserved device(s)."
    )
    count: None | str | int = core.Field(
        default=None,
        description="If 'count' is set to 'all' or not specified, Compose reserves all devices that satisfy the requested capabilities. Otherwise, Compose reserves at least the number of devices specified"
    )
    device_ids: list[str] = core.Field(
        default_factory=list,
        description="If device_ids is set, Compose reserves devices with the specified IDs provided they satisfy the requested capabilities. "
    )
    options: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Driver specific options."
    )


class Resource(cli.NoEmpty):
    cpus: None | int = core.Field(
        default=None,
        description="Limit or reservation for how much of the available CPU resources, as number of cores, a container can use."
    )
    memory: None | int = core.Field(
        default=None,
        description="Limit or reservation for how much of the available CPU resources, as number of cores, a container can use."
    )
    pids: None | int = core.Field(
        default=None,
        description="Tunes a container’s PIDs limit, set as an integer."
    )
    devices: list[Device] = core.Field(
        default_factory=list,
        description="Reservations of the devices a container."
    )


class Resources(cli.NoEmpty):
    limits: None | Resource = core.Field(None)
    reservations: None | Resource = core.Field(None)


class Restart(cli.NoEmpty):
    condition: None | str = core.Field(
        default=None,
        description="Restart condition."
    )
    delay: None | str = core.Field(
        default=None,
        description="How long to wait between restart attempts."
    )
    max_attempts: None | int = core.Field(
        default=None,
        description="How many times to attempt to restart a container before giving up (default: never give up)."
    )
    window: None | str = core.Field(
        default=None,
        description="How long to wait before deciding if a restart has succeeded."
    )


class Update(cli.NoEmpty):
    parallelism: None | int = core.Field(
        default=None,
        description="The number of containers to rollback at a time. If set to 0, all containers rollback simultaneously."
    )
    delay: None | str = core.Field(
        default=None,
        description="The time to wait between each container group's rollback (default 0s)."
    )
    failure_action: None | str = core.Field(
        default=None,
        description="What to do if a rollback fails. One of continue or pause (default pause)"
    )
    monitor: None | str = core.Field(
        default=None,
        description="Duration after each task update to monitor for failure (ns|us|ms|s|m|h) (default 0s)."
    )
    max_failure_ratio: None | int = core.Field(
        default=None,
        description="Failure rate to tolerate during a rollback (default 0)."
    )
    order: None | str = core.Field(
        default=None,
        description="Order of operations during rollbacks. One of stop-first (old task is stopped before starting new one), or start-first (new task is started first, and the running tasks briefly overlap) (default stop-first)."
    )


class Deploy(cli.NoEmpty):
    endpoint_mode: None | str = core.Field(
        default=None,
        description="Specifies a service discovery method for external clients connecting to a service."
    )
    labels: dict[str, str] = core.Field(
        default_factory=dict,
        description="Service metadata."
    )
    mode: None | str = core.Field(
        default=None,
        description="Replication model used to run the service on the platform."
    )
    placement: None | Placement = core.Field(
        default=None,
        description="Constraints and preferences for the platform to select a physical node to run service containers."
    )
    replicas: None | int = core.Field(
        default=None,
        description="If the service is replicated (which is the default), replicas specifies the number of containers that should be running at any given time."
    )
    resources: None | Resources = core.Field(
        default=None,
        description="Physical resource constraints for container to run on platform."
    )
    rollback_config: None | Update = core.Field(
        default=None,
        description="How the service should be rollbacked in case of a failing update."
    )
    update_config: None | Update = core.Field(
        default=None,
        description="How the service should be updated."
    )


class Watch(cli.NoEmpty):
    path: None | str | Path = core.Field(None)
    action: None | str = core.Field(None)
    target: None | str = core.Field(None)
    ignore: list[str] = core.Field(default_factory=list)


class Develop(cli.NoEmpty):
    watch: list[Watch] = core.Field(default_factory=list)


class EnvFile(cli.NoEmpty):
    path: Path | str = core.Field(
        description="Environment file path."
    )
    required: bool = core.Field(
        default=True,
        description="Is file required."
    )


class Extend(cli.NoEmpty):
    service: str = core.Field(
        description="The name of the service being referenced as a base."
    )
    file: None | Path = core.Field(
        default=None,
        description="The location of a Compose configuration file defining that service."
    )


class Healthcheck(cli.NoEmpty):
    test: list[str] = core.Field(
        description="Command to run to check health"
    )
    interval: str = core.Field(
        description="Time between running the check (ms|s|m|h) (default 0s)"
    )
    timeout: str = core.Field(
        description="Maximum time to allow one check to run (ms|s|m|h) (default 0s)"
    )
    retries: int = core.Field(
        description="Consecutive failures needed to report unhealthy"
    )
    start_period: str = core.Field(
        description="Start period for the container to initialize before starting health-retries countdown (ms|s|m|h) (default 0s)"
    )
    start_interval: str = core.Field(
        description="Start period for the container to initialize before starting health-retries countdown (ms|s|m|h) (default 0s)"
    )


class Logging(cli.NoEmpty):
    driver: str = core.Field(
        description="The logging driver."
    )
    options: dict[str, Any] = core.Field(
        description="The logging driver options."
    )


class SecretAccess(cli.NoEmpty):
    source: str
    target: str | Path
    uid: str
    gid: str
    mode: int


class StorageOpt(cli.NoEmpty):
    size: str = core.Field(
        description="Storage size."
    )


class Net(cli.NoEmpty):
    aliases: list[str] = core.Field(
        default_factory=list,
        description="Alternative hostnames for the service on the network. "
    )
    ipv4_address: None | str = core.Field(
        default=None,
        description="Static IP (v4) address for a service container when joining the network."
    )
    ipv6_address: None | str = core.Field(
        default=None,
        description="Static IP (v6) address for a service container when joining the network."
    )
    link_local_ips: list[str] = core.Field(
        default_factory=list,
        description="List of link-local IPs."
    )
    mac_address: None | str = core.Field(
        default=None,
        description="Sets the MAC address used by the service container when connecting to this particular network."
    )
    priority: None | int = core.Field(
        default=None,
        description="Indicates in which order Compose connects the service’s containers to its networks. If unspecified, the default value is 0."
    )


class ULimits(cli.NoEmpty):
    class Nofile(cli.NoEmpty):
        soft: int
        hard: int
    nproc: int
    nofile: Nofile


class Mount(cli.NoEmpty):
    class Info(cli.NoEmpty):
        nocopy: bool = True
    type: str
    source: Path | str
    target: Path | str
    volume: None | Info = None


class Volumes(cli.NoEmpty):
    mounts: list[Mount] = core.Field(default_factory=list)

    def volume(self, src: str | Path, dst: str | Path, nocopy: bool = None):
        self._add("volume", src, dst, nocopy)

    def bind(self, src: str | Path, dst: str | Path, nocopy: bool = None):
        self._add("bind", src, dst, nocopy)

    def tmpfs(self, src: str | Path, dst: str | Path, nocopy: bool = None):
        self._add("tmpfs", src, dst, nocopy)

    def npipe(self, src: str | Path, dst: str | Path, nocopy: bool = None):
        self._add("npipe", src, dst, nocopy)

    def add(self, mount: Mount):
        self.mounts.append(mount)

    def _add(self, t: str, src: str | Path, dst: str | Path, nocopy: bool = None):
        mount = Mount(type=t, source=str(src), target=str(dst))
        if nocopy is not None:
            mount.volume = Mount.Info(nocopy=nocopy)
        self.mounts.append(mount)


class Service(cli.NoEmpty):
    build: None | Build = core.Field(
        default=None,
        description="Defines either a path to a directory containing a Dockerfile, or a URL to a git repository."
    )
    blkio_config: None | BlockIo = core.Field(
        default=None,
        description="Set of configuration options to set block IO limits for a service."
    )
    cpu_count: None | int = core.Field(
        default=None,
        description="CPU CFS (Completely Fair Scheduler) period when a platform is based on Linux kernel."
    )
    cpu_period: None | int = core.Field(
        default=None,
        description="Limit CPU CFS (Completely Fair Scheduler) period"
    )
    cpu_percent: None | int = core.Field(
        default=None,
        description="Usable percentage of the available CPUs."
    )
    cpu_quota: None | int = core.Field(
        default=None,
        description="Limit CPU CFS (Completely Fair Scheduler) quota"
    )
    cpu_shares: None | int = core.Field(
        default=None,
        description="Service container's relative CPU weight versus other containers."
    )
    cpu_rt_period: None | int | str = core.Field(
        default=None,
        description="Limit the CPU real-time period in microseconds"
    )
    cpu_rt_runtime: None | int | str = core.Field(
        default=None,
        description="Limit the CPU real-time runtime in microseconds"
    )
    cpuset: None | str = core.Field(
        default=None,
        description="CPUs in which to allow execution (0-3, 0,1)"
    )
    cap_add: list[str] = core.Field(
        default_factory=list,
        description="Add Linux capabilities"
    )
    cap_drop: list[str] = core.Field(
        default_factory=list,
        description="Drop Linux capabilities"
    )
    cgroup: None | str = core.Field(
        default=None,
        description="Cgroup namespace to use (host|private)"
                    "   'host': Run the container in the Docker host's cgroup namespace"
                    "'private': Run the container in its own private cgroup namespace"
    )
    cgroup_parent: None | str = core.Field(
        default=None,
        description="Optional parent cgroup for the container"
    )
    command: None | list[str] = core.Field(
        default_factory=list,
        description="Overrides the default command declared by the container image, for example by Dockerfile's CMD."
    )
    configs: list[str] = core.Field(
        default_factory=list,
        description="Configs allow services to adapt their behaviour without the need to rebuild a Docker image. Services can only access configs when explicitly granted by the configs attribute"
    )
    container_name: None | str = core.Field(
        default=None,
        description="Service container name."
    )
    credential_spec: None | Credential = core.Field(
        default=None,
        description="Credential spec for a managed service account."
    )
    depends_on: None | list[str] | dict[str, Dependency] = core.Field(
        default=None,
        description="Service dependencies."
    )
    deploy: None | Deploy = core.Field(
        default=None,
        description="Deploy options."
    )
    develop: None | Develop = core.Field(
        default=None,
        description="Develop options."
    )
    device_cgroup_rules: list[str] = core.Field(
        default=None,
        description="Defines a list of device cgroup rules for this container."
    )
    devices: list[str] = core.Field(
        default_factory=list,
        description="List of device mappings for created containers."
    )
    dns: list[str] = core.Field(
        default_factory=list,
        description="Custom DNS servers to set on the container network interface configuration."
    )
    dns_opt: list[str] = core.Field(
        default_factory=list,
        description="Custom DNS options to be passed to the container’s DNS resolver (/etc/resolv.conf file on Linux)."
    )
    dns_search: list[str] = core.Field(
        default_factory=list,
        description="Custom DNS search domains to set on container network interface configuration."
    )
    domainname: None | str = core.Field(
        default=None,
        description="Custom domain name to use for the service container. It must be a valid RFC 1123 hostname."
    )
    entrypoint: list[str] = core.Field(
        default_factory=list,
        description="Entrypoint for the service container."
    )
    env_file: list[EnvFile] = core.Field(
        default_factory=list,
        description="Adds environment variables to the container based on the files content."
    )
    environment: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Environment variables set in the container."
    )
    expose: list[str] = core.Field(
        default_factory=list,
        description="The (incoming) port or a range of ports that Compose exposes from the container."
    )
    extends: None | Extend = core.Field(
        default=None,
        description="'extends' lets you share common configurations among different files, or even different projects entirely. With 'extends'   you can define a common set of service options in one place and refer to it from anywhere. You can refer to another Compose file and select a service you want to also use in your own application, with the ability to override some attributes for your own needs."
    )
    extra_hosts: dict[str, str] = core.Field(
        default_factory=dict,
        description="Adds hostname mappings at build-time. Use the same syntax as extra_hosts."
    )
    group_add: list[str] = core.Field(
        default_factory=list,
        description="Additional groups, by name or number, which the user inside the container must be a member of."
    )
    healthcheck: None | Healthcheck = core.Field(
        default=None,
        description="Healthcheck options."
    )
    hostname: None | str = core.Field(
        default=None,
        description="Custom host name to use for the service container. It must be a valid RFC 1123 hostname."
    )
    image: None | str = core.Field(
        default=None,
        description="Image name."
    )
    init: None | bool = core.Field(
        default=None,
        description="Runs an init process (PID 1) inside the container that forwards signals and reaps processes."
    )
    ipc: None | str = core.Field(
        default=None,
        description="IPC isolation mode set by the service container."
    )
    isolation: None | str = core.Field(
        default=None,
        description="Specifies a container’s isolation technology. Supported values are platform specific."
    )
    labels: dict[str, str] = core.Field(
        default_factory=dict,
        description="Container metadata."
    )
    links: list[str] = core.Field(
        default_factory=list,
        description="Network link to containers in another service."
    )
    logging: None | Logging = core.Field(
        default=None,
        description="The logging configuration for the service."
    )
    mac_address: None | str = core.Field(
        default=None,
        description="MAC address for the service container."
    )
    mem_swappiness: None | int = core.Field(
        default=None,
        description="defines as a percentage, a value between 0 and 100, for the host kernel to swap out anonymous memory pages used by a container."
    )
    memswap_limit: None | int = core.Field(
        default=None,
        description="Amount of memory the container is allowed to swap to disk. This is a modifier attribute that only has meaning if 'memory' is also set. Using swap lets the container write excess memory requirements to disk when the container has exhausted all the memory that is available to it. There is a performance penalty for applications that swap memory to disk often."
    )
    network_mode: None | str = core.Field(
        default=None,
        description="Sets a service container's network mode."
    )
    networks: dict[str, Net] = core.Field(
        default_factory=dict,
        description="Networks that service containers are attached to, referencing entries under the top-level networks key."
    )
    oom_kill_disable: None | bool = core.Field(
        default=None,
        description="Is set, Compose configures the platform so it won't kill the container in case of memory starvation."
    )
    oom_score_adj: None | int = core.Field(
        default=None,
        description="Tunes the preference for containers to be killed by platform in case of memory starvation. Value must be within -1000,1000 range."
    )
    pid: None | int = core.Field(
        default=None,
        description="Sets the PID mode for container created by Compose. Supported values are platform specific."
    )
    platform: None | str = core.Field(
        default=None,
        description="Target platform the containers for the service run on."
    )
    ports: list[str] = core.Field(
        default_factory=list,
        description="Exposes container ports. NOTE: port mapping must not be used with 'network_mode: host' otherwise a runtime error occurs."
    )
    privileged: None | bool = core.Field(
        default=None,
        description="Configures the service container to run with elevated privileges. Support and actual impacts are platform specific."
    )
    profiles: list[str] = core.Field(
        default_factory=list,
        description="A list of named profiles for the service to be enabled under. If unassigned, the service is always started but if assigned, it is only started if the profile is activated."
    )
    pull_policy: None | str = core.Field(
        default=None,
        description="Defines the decisions Compose makes when it starts to pull images"
    )
    read_only: None | bool = core.Field(
        default=None,
        description="Configures the service container to be created with a read-only filesystem."
    )
    restart: None | str = core.Field(
        default=None,
        description="Defines the policy that the platform applies on container termination."
    )
    runtime: None | str = core.Field(
        default=None,
        description="Specifies which runtime to use for the service’s containers."
    )
    scale: None | int = core.Field(
        default=None,
        description="specifies the default number of containers to deploy for this service. When both are set, 'scale' must be consistent with the 'replicas' attribute in the Deploy Specification."
    )
    secrets: list[str] | list[SecretAccess] = core.Field(
        default_factory=list,
        description="Grants access to sensitive data defined by secrets on a per-service basis."
    )
    security_opt: list[str] = core.Field(
        default_factory=list,
        description="Overrides the default labeling scheme for each container."
    )
    shm_size: None | str = core.Field(
        default=None,
        description="Configures the size of the shared memory (/dev/shm partition on Linux) allowed by the service container. It's specified as a byte value."
    )
    stdin_open: None | bool = core.Field(
        default=None,
        description="Configures a service containers to run with an allocated stdin."
    )
    stop_grace_period: None | str = core.Field(
        default=None,
        description="Specifies how long Compose must wait when attempting to stop a container if it doesn't handle SIGTERM (or whichever stop signal has been specified with stop_signal), before sending SIGKILL. It's specified as a duration."
    )
    stop_signal: None | str = core.Field(
        default=None,
        description="Defines the signal that Compose uses to stop the service containers. If unset containers are stopped by Compose by sending SIGTERM."
    )
    storage_opt: None | StorageOpt = core.Field(
        default=None,
        description="Storage options."
    )
    sysctl: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Defines kernel parameters to set in the container."
    )
    tmpfs: list[str] = core.Field(
        default_factory=list,
        description="Mounts a temporary file system inside the container."
    )
    tty: None | bool = core.Field(
        default=None,
        description="Configures service container to run with a TTY."
    )
    ulimits: None | ULimits = core.Field(
        default=None,
        description="Overrides the default ulimits for a container. It's specified either as an integer for a single limit or as mapping for soft/hard limits."
    )
    user: None | str = core.Field(
        default=None,
        description="Overrides the user used to run the container process. The default is set by the image (i.e. Dockerfile USER). If it's not set, then root."
    )
    userns_mode: None | str = core.Field(
        default=None,
        description="The user namespace for the service. Supported values are platform specific and may depend on platform configuration."
    )
    uts: None | str = core.Field(
        default=None,
        description="Configures the UTS namespace mode set for the service container. When unspecified it is the runtime's decision to assign a UTS namespace, if supported. "
    )
    volumes: Volumes = core.Field(
        default_factory=Volumes,
        description="Mounts host paths or named volumes that are accessible by service containers. You can use volumes to define multiple types of mounts; volume, bind, tmpfs, or npipe."
    )
    volumes_from: list[str] = core.Field(
        default_factory=list,
        description="Mounts all of the volumes from another service or container. You can optionally specify read-only access 'ro' or read-write 'rw'. If no access level is specified, then read-write access is used."
    )
    working_dir: None | Path | str = core.Field(
        default=None,
        description="Overrides the container's working directory which is specified by the image, for example Dockerfile's WORKDIR"
    )

    @core.field.serializer("volumes")
    def serialize_volumes(self, value: Volumes, _info):
        return value.mounts


# ####################################################################################
# Network models
# ####################################################################################

class IpamConfig(cli.NoEmpty):
    subnet: None | str = core.Field(
        default=None,
        description="Subnet in CIDR format that represents a network segment."
    )
    ip_range: None | str = core.Field(
        default=None,
        description="Range of IPs from which to allocate container IPs."
    )
    gateway: None | str = core.Field(
        default=None,
        description="IPv4 or IPv6 gateway for the master subnet."
    )
    aux_addresses: dict[str, str] = core.Field(
        default=None,
        description="Auxiliary IPv4 or IPv6 addresses used by Network driver, as a mapping from hostname to IP."
    )


class IPAM(cli.NoEmpty):
    driver: None | str = core.Field(
        default=None,
        description="Custom IPAM driver, instead of the default."
    )
    config: None | IpamConfig = core.Field(
        default=None,
        description="IPAM config."
    )
    options: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Driver-specific options as a key-value mapping."
    )


class Network(cli.NoEmpty):
    driver: None | str = core.Field(
        default=None,
        description="Specifies which driver should be used for this network."
    )
    driver_opts: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Specifies a list of options as key-value pairs to pass to the driver."
    )
    attachable: None | bool = core.Field(
        default=None,
        description="If it is set to true, then standalone containers should be able to attach to this network, in addition to services. If a standalone container attaches to the network, it can communicate with services and other standalone containers that are also attached to the network."
    )
    enable_ipv6: None | bool = core.Field(
        default=None,
        description="Enables IPv6 networking."
    )
    external: None | bool = core.Field(
        default=None,
        description="Is network external."
    )
    ipam: None | IPAM = core.Field(
        default=None,
        description="Specifies a custom IPAM configuration."
    )
    internal: None | bool = core.Field(
        default=None,
        description="By default, Compose provides external connectivity to networks. 'internal', when set to true, allows you to create an externally isolated network."
    )
    labels: None | dict[str, str] = core.Field(
        default_factory=dict,
        description="Network metadata."
    )
    name: None | str = core.Field(
        default=None,
        description="Sets a custom name for the network. The name field can be used to reference networks which contain special characters. The name is used as is and is not scoped with the project name."
    )


# ####################################################################################
# Volumes models
# ####################################################################################

class Volume(cli.NoEmpty):
    driver: None | str = core.Field(
        default=None,
        description="Specifies which volume driver should be used."
    )
    driver_opts: dict[str, Any] = core.Field(
        default_factory=dict,
        description="Specifies a list of options as key-value pairs to pass to the driver for this volume."
    )
    external: None | bool = core.Field(
        default=None,
        description="Is volume external."
    )
    labels: None | dict[str, str] = core.Field(
        default_factory=dict,
        description="Volume metadata."
    )
    name: None | str = core.Field(
        default=None,
        description="Sets a custom name for a volume. The name field can be used to reference volumes that contain special characters. The name is used as is and is not scoped with the stack name."
    )


# ####################################################################################
# Configs models
# ####################################################################################

class Config(cli.NoEmpty):
    file: None | str = core.Field(
        default=None,
        description="The config is created with the contents of the file at the specified path."
    )
    environment: dict[str, Any] = core.Field(
        default_factory=dict,
        description="The config content is created with the value of an environment variable."
    )
    content: list[str] = core.Field(
        default_factory=list,
        description="The content is created with the inlined value."
    )
    external: None | bool = core.Field(
        default=None,
        description="Is config external."
    )
    name: None | str = core.Field(
        default=None,
        description="The name of the config object in the container engine to look up. This field can be used to reference configs that contain special characters. The name is used as is and will not be scoped with the project name."
    )

    @core.field.serializer("content")
    def serialize_content(self, value: list[str], _info):
        if not value:
            return ""
        return "\n".join(value)


# ####################################################################################
# Secrets models
# ####################################################################################

class Secret(cli.NoEmpty):
    file: None | str = core.Field(
        default=None,
        description="The secret is created with the contents of the file at the specified path."
    )
    environment: dict[str, Any] = core.Field(
        default_factory=dict,
        description="The secret is created with the value of an environment variable."
    )


# ####################################################################################
# File
# ####################################################################################

class File(cli.NoEmpty):
    services: dict[str, Service] = core.Field(
        default_factory=dict,
        description="List of the services."
    )
    networks: dict[str, Network] = core.Field(
        default_factory=dict,
        description="List of the networks."
    )
    volumes: dict[str, Volume] = core.Field(
        default_factory=dict,
        description="List of the volumes."
    )
    configs: dict[str, Config] = core.Field(
        default_factory=dict,
        description="List of the configs."
    )
    secrets: dict[str, Config] = core.Field(
        default_factory=dict,
        description="List of the secrets."
    )
    path: Path = core.Field(
        default=None,
        description="Output directory path.",
        exclude=True
    )
    name: str = core.Field(
        default="docker-compose.yaml",
        description="Output file name.",
        exclude=True
    )

    @property
    def file(self) -> Path:
        if self.path is None:
            raise ValueError("Composefile: output path is None")
        return self.path / self.name

    def __repr__(self):
        return f"composefile://{str(self.file)}"

    def __str__(self):
        return self.text()

    def text(self) -> str:
        data = self.model_dump()
        keys = []
        for k, v in data.items():
            if not v:
                keys.append(k)
        for k in keys:
            data.pop(k)
        return yaml.safe_dump(data, sort_keys=False)

    def save(self):
        file = self.file
        if not file.parent.exists():
            os.makedirs(file.parent)
        text = self.text()
        with open(file, "w") as stream:
            stream.write(text)
