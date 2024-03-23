import platform

from umk import core


class Platform(core.Model):
    os: str = core.Field(
        default="",
        description="OS name"
    )
    arch: str = core.Field(
        default="",
        description="Architecture"
    )

    @property
    def unix(self) -> bool:
        return self.os in ("linux", "darwin")

    @property
    def linux(self) -> bool:
        return self.os == "linux"

    @property
    def windows(self) -> bool:
        return self.os == "windows"

    @property
    def x64(self) -> bool:
        return self.arch in ("amd64", "x86_64", "arm64")


def create() -> Platform:
    result = Platform()
    result.os = platform.system().lower()
    if result.os == "win32":
        result.os = "windows"
    result.arch = platform.machine()
    return result
