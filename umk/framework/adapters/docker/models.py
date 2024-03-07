from typing import Any

from umk import core


# from docker.models.images import Image
# from docker.models.containers import Container
# from docker.models.networks import Network
# from docker.models.volumes import Volume
# from docker.models.swarm import Swarm
# from docker.models.secrets import Secret


def short_id(identifier: str) -> str:
    if not identifier:
        return ""
    return identifier.split(":")[-1][:12]


class Filter(dict):
    def __str__(self):
        return " ".join([f"{k}={v}" for k, v in self.items()])


class Image:
    @property
    def id(self) -> str:
        result = self.details.get("Id")
        result = result if result else ""
        return short_id(result)

    @property
    def labels(self) -> dict[str, str]:
        result = self.details['Config'].get('Labels')
        return result if result else {}

    @property
    def tags(self) -> list[str]:
        tags = self.details.get('RepoTags')
        if tags is None:
            tags = []
        return [tag for tag in tags if tag != '<none>:<none>']

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    @core.typeguard
    def __init__(self, details: None | dict[str, Any] = None):
        self._details = details if details else {}


class Container:
    @property
    def id(self) -> str:
        result = self.details.get("Id")
        return short_id(result if result else "")

    @property
    def name(self) -> str:
        return self.details.get("Name", "").lstrip("/")

    @property
    def labels(self) -> dict[str, str]:
        result = self.details['Config'].get('Labels')
        return result if result else {}

    @property
    def image(self) -> str:
        result = self.details.get("Image")
        return short_id(result if result else "")

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    @property
    def status(self) -> str:
        state = self.details.get("State")
        if not state:
            return ""
        result = state.get("Status")
        if not result:
            result = ""
        return result

    @core.typeguard
    def __init__(self, details: None | dict[str, Any] = None):
        self._details = details if details else {}


if __name__ == '__main__':
    from docker.types.containers import Ulimit
    from docker.types.services import Mount, DriverConfig

    m = Mount(
        target="trg",
        source="src",
        type="bind",
        read_only=True,
        consistency="consis",
        propagation="propg",
        no_copy=True,
        labels={"hello": "world"},
        driver_config=DriverConfig("driver", {"opt": "23"}),
        tmpfs_size=23,
        tmpfs_mode=2
    )

    print(m)
