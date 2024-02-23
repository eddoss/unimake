from beartype.typing import Optional, Any
from textwrap import dedent
from umk import core
from umk.framework.system import environs as envs
from umk.framework.system.shell import Shell
from umk.framework.filesystem import Path
from umk.framework.remote.interface import Interface
from umk.framework.remote.docker.container import Container
from umk.framework.adapters.docker import file as dockerfile


class ContainerParams(core.Object):
    image: str = core.Field(
        default="",
        description="The image to run",
    )
    auto_remove: Optional[bool] = core.Field(
        default=None,
        description="Enable auto-removal of the container on daemon side when the container's process exits."
    )
    blkio_weight_device: list[dict[str, Any]] = core.Field(
        default_factory=list,
        description='Block IO weight (relative device weight) in the form of: ``[{"Path": "device_path", "Weight": weight}]``.'
    )
    blkio_weight: Optional[int] = core.Field(
        default=None,
        description="Block IO weight (relative weight), accepts a weight value between 10 and 1000."
    )
    cap_add: list[str] = core.Field(
        description='Add kernel capabilities. For example, ``["SYS_ADMIN", "MKNOD"]``.'
    )
    cap_drop: list[str] = core.Field(
        default_factory=list,
        description="Drop kernel capabilities.",
    )
    cgroup_parent: Optional[str] = core.Field(
        default=None,
        description="Override the default parent cgroup.",
    )
    cgroupns: Optional[str] = core.Field(
        default=None,
        description="Override the default cgroup namespace mode for the container. One of:"
                    "- ``private`` the container runs in its own private cgroup namespace."
                    "- ``host`` use the host system's cgroup namespace."
    )
    cpu_count: Optional[int] = core.Field(
        default=None,
        description="Number of usable CPUs (Windows only)."
    )
    cpu_percent: Optional[int] = core.Field(
        default=None,
        description="Usable percentage of the available CPUs (Windows only)."
    )
    cpu_period: Optional[int] = core.Field(
        default=None,
        description="The length of a CPU period in microseconds."
    )
    cpu_quota: Optional[int] = core.Field(
        default=None,
        description="Microseconds of CPU time that the container can get in a CPU period."
    )
    cpu_rt_period: Optional[int] = core.Field(
        default=None,
        description="Limit CPU real-time period in microseconds."
    )
    cpu_rt_runtime: Optional[int] = core.Field(
        default=None,
        description="Limit CPU real-time runtime in microseconds."
    )
    cpu_shares: Optional[int] = core.Field(
        default=None,
        description="CPU shares (relative weight)."
    )
    cpuset_cpus: Optional[str] = core.Field(
        default=None,
        description="CPUs in which to allow execution (``0-3``, ``0,1``)."
    )
    cpuset_mems: Optional[str] = core.Field(
        default=None,
        description="Memory nodes (MEMs) in which to allow execution (``0-3``, ``0,1``). Only effective on NUMA systems."
    )
    detach: Optional[bool] = core.Field(
        default=None,
        description="Run container in the background and return a :py:class:`Container` object."
    )
    device_cgroup_rules: list[str] = core.Field(
        default_factory=list,
        description="A list of cgroup rules to apply to the container."
    )
# device_read_bps: Limit read rate (bytes per second) from a device in the form of: `[{"Path": "device_path", "Rate": rate}]`
# device_read_iops: Limit read rate (IO per second) from a device.
# device_write_bps: Limit write rate (bytes per second) from a device.
# device_write_iops: Limit write rate (IO per second) from a device.
# devices (:py:class:`list`): Expose host devices to the container, as a list of strings in the form ``<path_on_host>:<path_in_container>:<cgroup_permissions>``.
#     For example, ``/dev/sda:/dev/xvda:rwm`` allows the container
#     to have read-write access to the host's ``/dev/sda`` via a
#     node named ``/dev/xvda`` inside the container.
# device_requests (:py:class:`list`): Expose host resources such as GPUs to the container, as a list of :py:class:`docker.types.DeviceRequest` instances.
# dns (:py:class:`list`): Set custom DNS servers.
# dns_opt (:py:class:`list`): Additional options to be added to the container's ``resolv.conf`` file.
# dns_search (:py:class:`list`): DNS search domains.
# domainname (str or list): Set custom DNS search domains.
# entrypoint (str or list): The entrypoint for the container.
# environment (dict or list): Environment variables to set inside the container, as a dictionary or a list of strings in the format ``["SOMEVARIABLE=xxx"]``.
# extra_hosts (dict): Additional hostnames to resolve inside the container, as a mapping of hostname to IP address.
# group_add (:py:class:`list`): List of additional group names and/or IDs that the container process will run as.
# healthcheck (dict): Specify a test to perform to check that the container is healthy. The dict takes the following keys:
#     - test (:py:class:`list` or str): Test to perform to determine
#         container health. Possible values:
#         - Empty list: Inherit healthcheck from parent image
#         - ``["NONE"]``: Disable healthcheck
#         - ``["CMD", args...]``: exec arguments directly.
#         - ``["CMD-SHELL", command]``: Run command in the system's
#           default shell.
#         If a string is provided, it will be used as a ``CMD-SHELL``
#         command.
#     - interval (int): The time to wait between checks in
#       nanoseconds. It should be 0 or at least 1000000 (1 ms).
#     - timeout (int): The time to wait before considering the check
#       to have hung. It should be 0 or at least 1000000 (1 ms).
#     - retries (int): The number of consecutive failures needed to
#         consider a container as unhealthy.
#     - start_period (int): Start period for the container to
#         initialize before starting health-retries countdown in
#         nanoseconds. It should be 0 or at least 1000000 (1 ms).
# hostname (str): Optional hostname for the container.
# init (bool): Run an init inside the container that forwards signals and reaps processes
# init_path (str): Path to the docker-init binary
# ipc_mode (str): Set the IPC mode for the container.
# isolation (str): Isolation technology to use. Default: `None`.
# kernel_memory (int or str): Kernel memory limit
# labels (dict or list): A dictionary of name-value labels (e.g. ``{"label1": "value1", "label2": "value2"}``) or a list of names of labels to set with empty values (e.g. ``["label1", "label2"]``)
# links (dict): Mapping of links using the ``{'container': 'alias'}`` format. The alias is optional. Containers declared in this dict will be linked to the new container using the provided alias. Default: ``None``.
# log_config (LogConfig): Logging configuration.
# lxc_conf (dict): LXC config.
# mac_address (str): MAC address to assign to the container.
# mem_limit (int or str): Memory limit. Accepts float values (which represent the memory limit of the created container in bytes) or a string with a units identification char (``100000b``, ``1000k``, ``128m``, ``1g``). If a string is specified without a units character, bytes are assumed as an intended unit.
# mem_reservation (int or str): Memory soft limit.
# mem_swappiness (int): Tune a container's memory swappiness behavior. Accepts number between 0 and 100.
# memswap_limit (str or int): Maximum amount of memory + swap a container is allowed to consume.
# mounts (:py:class:`list`): Specification for mounts to be added to the container. More powerful alternative to ``volumes``. Each item in the list is expected to be a :py:class:`docker.types.Mount` object.
# name (str): The name for this container.
# nano_cpus (int):  CPU quota in units of 1e-9 CPUs.
# network (str): Name of the network this container will be connected to at creation time. You can connect to additional networks using :py:meth:`Network.connect`. Incompatible with ``network_mode``.
# network_disabled (bool): Disable networking.
# network_mode (str): One of:
#     - ``bridge`` Create a new network stack for the container on the bridge network.
#     - ``none`` No networking for this container.
#     - ``container:<name|id>`` Reuse another container's network stack.
#     - ``host`` Use the host network stack. This mode is incompatible with ``ports``. Incompatible with ``network``.
# networking_config (Dict[str, EndpointConfig]): Dictionary of EndpointConfig objects for each container network. The key is the name of the network. Defaults to ``None``. Used in conjuction with ``network``. Incompatible with ``network_mode``.
# oom_kill_disable (bool): Whether to disable OOM killer.
# oom_score_adj (int): An integer value containing the score given to the container in order to tune OOM killer preferences.
# pid_mode (str): If set to ``host``, use the host PID namespace inside the container.
# pids_limit (int): Tune a container's pids limit. Set ``-1`` for unlimited.
# platform (str): Platform in the format ``os[/arch[/variant]]``. Only used if the method needs to pull the requested image.
# ports (dict): Ports to bind inside the container.
#     The keys of the dictionary are the ports to bind inside the container, either as an integer or a string in the form ``port/protocol``, where the protocol is either ``tcp``, ``udp``, or ``sctp``.
#     The values of the dictionary are the corresponding ports to open on the host, which can be either:
#     - The port number, as an integer. For example, ``{'2222/tcp': 3333}`` will expose port 2222 inside the container as port 3333 on the host.
#     - ``None``, to assign a random host port. For example, ``{'2222/tcp': None}``.
#     - A tuple of ``(address, port)`` if you want to specify the host interface. For example, ``{'1111/tcp': ('127.0.0.1', 1111)}``.
#     - A list of integers, if you want to bind multiple host ports to a single container port. For example, ``{'1111/tcp': [1234, 4567]}``.
#     Incompatible with ``host`` network mode.
# privileged (bool): Give extended privileges to this container.
# publish_all_ports (bool): Publish all ports to the host.
# read_only (bool): Mount the container's root filesystem as read only.
# remove (bool): Remove the container when it has finished running. Default: ``False``.
# restart_policy (dict): Restart the container when it exits.
#     Configured as a dictionary with keys:
#     - ``Name`` One of ``on-failure``, or ``always``.
#     - ``MaximumRetryCount`` Number of times to restart the
#       container on failure.
#     For example:
#     ``{"Name": "on-failure", "MaximumRetryCount": 5}``
# runtime (str): Runtime to use with this container.
# security_opt (:py:class:`list`): A list of string values to customize labels for MLS systems, such as SELinux.
# shm_size (str or int): Size of /dev/shm (e.g. ``1G``).
# stdin_open (bool): Keep ``STDIN`` open even if not attached.
# stdout (bool): Return logs from ``STDOUT`` when ``detach=False``. Default: ``True``.
# stderr (bool): Return logs from ``STDERR`` when ``detach=False``. Default: ``False``.
# stop_signal (str): The stop signal to use to stop the container (e.g. ``SIGINT``).
# storage_opt (dict): Storage driver options per container as a key-value mapping.
# stream (bool): If true and ``detach`` is false, return a log generator instead of a string. Ignored if ``detach`` is true. Default: ``False``.
# sysctls (dict): Kernel parameters to set in the container.
# tmpfs (dict): Temporary filesystems to mount, as a dictionary mapping a path inside the container to options for that path.
#     For example:
#     .. code-block:: python
#         {
#             '/mnt/vol2': '',
#             '/mnt/vol1': 'size=3G,uid=1000'
#         }
#
# tty (bool): Allocate a pseudo-TTY.
# ulimits (:py:class:`list`): Ulimits to set inside the container,
#     as a list of :py:class:`docker.types.Ulimit` instances.
# use_config_proxy (bool): If ``True``, and if the docker client
#     configuration file (``~/.docker/config.json`` by default)
#     contains a proxy configuration, the corresponding environment
#     variables will be set in the container being built.
# user (str or int): Username or UID to run commands as inside the
#     container.
# userns_mode (str): Sets the user namespace mode for the container
#     when user namespace remapping option is enabled. Supported
#     values are: ``host``
# uts_mode (str): Sets the UTS namespace mode for the container.
#     Supported values are: ``host``
# version (str): The version of the API to use. Set to ``auto`` to
#     automatically detect the server's version. Default: ``1.35``
# volume_driver (str): The name of a volume driver/plugin.
# volumes (dict or list): A dictionary to configure volumes mounted
#     inside the container. The key is either the host path or a
#     volume name, and the value is a dictionary with the keys:
#
#     - ``bind`` The path to mount the volume inside the container
#     - ``mode`` Either ``rw`` to mount the volume read/write, or
#       ``ro`` to mount it read-only.
#
#     For example:
#
#     .. code-block:: python
#
#         {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
#          '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}
#
#     Or a list of strings which each one of its elements specifies a
#     mount volume.
#
#     For example:
#
#     .. code-block:: python
#
#         ['/home/user1/:/mnt/vol2','/var/www:/mnt/vol1']
#
# volumes_from (:py:class:`list`): List of container names or IDs to
#     get volumes from.
# working_dir (str): Path to the working directory.

class BuildParams(core.Object):
    host: dict[str, str] = core.Field(default_factory=dict)
    args: dict[str, str] = core.Field(default_factory=dict)
    cache: list[str] = core.Field(default_factory=list)
    cgroup_parent: Optional[str] = None
    compress: Optional[bool] = None
    cpu_period: Optional[int] = None
    cpu_quota: Optional[int] = None
    cpu_shares: Optional[int] = None
    cpuset_cpus: Optional[str] = None
    cpuset_mems: Optional[str] = None


class File(Container):
    path: Path = core.Field(
        description="Dockerfile path",
        default=Path("Dockerfile")
    )

    def build(self, **kwargs):
        pass

    def destroy(self, **kwargs):
        super().destroy(**kwargs)

    def up(self, **kwargs):
        super().up(**kwargs)

    def down(self, **kwargs):
        super().down(**kwargs)

    def _register_properties(self):
        super()._register_properties()
        self._properties.add("path")

